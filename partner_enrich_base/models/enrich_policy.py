# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

"""Field-group policy: who is allowed to write which group.

The old code decided conflicts by install order — ``crm_allabolag`` called
``super()`` *after* writing, so whichever module happened to be installed last
won. That is not a decision, it is an accident. Here the precedence is written
down per field group:

``manual``
    Never write this group automatically. The values a user typed stand.

``fill_empty``
    Write only where the field is currently empty. This is the default: it makes
    enrichment additive, so a second run can never destroy a first run's result
    or a hand-typed correction.

``prefer:<provider>``
    This provider's value wins even over an existing value — but only for the
    groups it actually returns data for. Another provider can still fill a group
    that ``<provider>`` left out, because "prefer" is about conflicts, not about
    exclusivity.

An unknown provider key in ``prefer:`` is a configuration mistake, not a reason
to fail an enrichment run: it is logged and falls back to ``fill_empty``.
"""

import logging

from odoo import api, models

from .enrich_format import (
    CANONICAL_GROUPS,
    FIELD_GROUP,
    empty,
)

_logger = logging.getLogger(__name__)

POLICY_MANUAL = 'manual'
POLICY_FILL_EMPTY = 'fill_empty'
POLICY_PREFER = 'prefer:'

VALID_POLICIES = (POLICY_MANUAL, POLICY_FILL_EMPTY)

#: Parameter name per group, e.g. ``partner_enrich.policy.identity``.
PARAM_POLICY = 'partner_enrich.policy.%s'

#: Provider order parameter (comma separated).
PARAM_PROVIDER_ORDER = 'partner_enrich.provider_order'

#: Default provider order. The first provider is the one whose values win when
#: two providers both have something to say and neither is preferred.
DEFAULT_PROVIDER_ORDER = 'foretagssok,allabolag'


class ResPartnerEnrichPolicy(models.AbstractModel):
    """Dispatcher and policy helpers for partner enrichment.

    An abstract model rather than loose methods so the logic has a name and can
    be tested without a partner record.
    """

    _name = 'res.partner.enrich.policy'
    _description = 'Partner Enrichment Policy'

    # -- Provider registry ---------------------------------------------------

    @api.model
    def _enrich_provider_keys(self):
        """The provider keys to try, in priority order.

        Read from ``partner_enrich.provider_order``. When the parameter is
        unset or empty we fall back to :data:`DEFAULT_PROVIDER_ORDER` rather
        than to "every module that registered", because alphabetical order is
        not a priority order — a provider added later would silently outrank
        the one the operator chose.
        """
        raw = self.env['ir.config_parameter'].sudo().get_str(
            PARAM_PROVIDER_ORDER, default='',
        )
        raw = (raw or '').strip() or DEFAULT_PROVIDER_ORDER
        keys = [key.strip() for key in raw.split(',') if key.strip()]
        if not keys:
            keys = [key.strip() for key in DEFAULT_PROVIDER_ORDER.split(',')]
        return keys

    # -- Policy --------------------------------------------------------------

    @api.model
    def _enrich_policy(self, group):
        """The policy for one field group.

        Returns ``(mode, provider)`` where ``mode`` is one of ``manual``,
        ``fill_empty``, ``prefer`` and ``provider`` is the preferred provider
        key (``None`` unless ``mode`` is ``prefer``).
        """
        raw = self.env['ir.config_parameter'].sudo().get_str(
            PARAM_POLICY % group, default='',
        )
        raw = (raw or '').strip()

        if not raw:
            return POLICY_FILL_EMPTY, None

        if raw == POLICY_MANUAL:
            return POLICY_MANUAL, None

        if raw == POLICY_FILL_EMPTY:
            return POLICY_FILL_EMPTY, None

        if raw.startswith(POLICY_PREFER):
            provider = raw[len(POLICY_PREFER):].strip()
            if not provider:
                _logger.warning(
                    "Enrichment policy for group %r is %r without a provider "
                    "name — falling back to %s.",
                    group, raw, POLICY_FILL_EMPTY,
                )
                return POLICY_FILL_EMPTY, None
            if provider not in self._enrich_provider_keys():
                _logger.warning(
                    "Enrichment policy for group %r prefers %r, which is not "
                    "in the provider order (%s) — falling back to %s.",
                    group, provider, ', '.join(self._enrich_provider_keys()),
                    POLICY_FILL_EMPTY,
                )
                return POLICY_FILL_EMPTY, None
            return 'prefer', provider

        _logger.warning(
            "Unknown enrichment policy %r for group %r — falling back to %s. "
            "Valid values: %s, %s, %s<provider>.",
            raw, group, POLICY_FILL_EMPTY, POLICY_MANUAL, POLICY_FILL_EMPTY,
            POLICY_PREFER,
        )
        return POLICY_FILL_EMPTY, None

    @api.model
    def _enrich_all_policies(self):
        """Every group's policy, as ``{group: (mode, provider)}``."""
        return {group: self._enrich_policy(group) for group in CANONICAL_GROUPS}

    # -- Resolution ----------------------------------------------------------

    @api.model
    def _enrich_resolve(self, collected, current):
        """Decide the final value per key.

        ``collected`` is ``[(provider_key, canonical_dict), …]`` in priority
        order (the order of :meth:`_enrich_provider_keys`). ``current`` is a
        mapping of canonical key -> the value currently stored on the record.

        Returns ``{canonical_key: (value, provider_key)}`` — only the keys that
        should actually be written, with the provider that won them.
        """
        result = {}

        # Build per-group candidate lists first: precedence is per group, and a
        # group's policy must not be re-read once per key.
        by_group = {group: [] for group in CANONICAL_GROUPS}
        for provider_key, data in collected:
            for key, value in data.items():
                # ``clean()`` already dropped empties and unknown keys, but a
                # provider may call us directly, so guard again.
                if not key or key not in FIELD_GROUP:
                    continue
                by_group[FIELD_GROUP[key]].append((provider_key, key, value))

        for group, candidates in by_group.items():
            if not candidates:
                continue
            mode, preferred = self._enrich_policy(group)

            if mode == POLICY_MANUAL:
                continue

            if mode == 'prefer':
                preferred_candidates = [
                    (provider_key, key, value)
                    for provider_key, key, value in candidates
                    if provider_key == preferred
                ]
                if preferred_candidates:
                    for provider_key, key, value in preferred_candidates:
                        result[key] = (value, provider_key)
                    continue
                # The preferred provider had nothing for this group — let the
                # ordinary precedence fill the gaps instead of leaving the
                # group empty just because the favourite was silent.
                _logger.debug(
                    "Enrichment: preferred provider %r returned nothing for "
                    "group %r — using normal precedence.", preferred, group,
                )

            # fill_empty / prefer-with-no-data: first provider that has the key
            # wins, and only where the record has no value yet.
            for provider_key, key, value in candidates:
                if key in result:
                    continue
                if not empty(current.get(key)):
                    continue
                result[key] = (value, provider_key)

        return result

