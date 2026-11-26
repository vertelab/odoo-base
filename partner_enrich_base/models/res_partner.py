# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo SA, Open Source Management Solution, third party addon
#    Copyright (C) 2024- Vertel Sverige AB (<https://vertel.se>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import json
import logging
import re

from odoo import api, fields, models, tools

from odoo.addons.partner_autocomplete.models.res_company import COMPANY_AC_TIMEOUT

from .enrich_format import LEAD_FIELD_MAP, PARTNER_FIELD_MAP, clean, empty, pick


_logger = logging.getLogger(__name__)

#: Set by this module series to make the intent explicit: company data comes
#: from our own providers, not from the IAP service.
COMPANY_NO_IAP = True

#: Anything that is not a digit. Swedish organisation numbers are written
#: ``NNNNNN-NNNN``, ``NNNNNNNNNN``, ``SE NNNNNN NNNN 01`` and with non-breaking
#: spaces, and all of those must normalise to the same value.
_NON_DIGIT = re.compile(r'\D')


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # -- Enrichment bookkeeping ---------------------------------------------
    enrich_fetched_at = fields.Datetime(
        string='Enriched At',
        readonly=True,
        help='When the enrichment data on this contact was last refreshed.',
    )
    enrich_provider = fields.Char(
        string='Enriched By',
        readonly=True,
        help='Which provider supplied the current enrichment data.',
    )
    enrich_raw = fields.Text(
        string='Enrichment Raw Data',
        readonly=True,
        help='Provider response, kept for troubleshooting and for re-applying '
             'without another API call.',
    )

    # -- Normalisation -------------------------------------------------------

    @api.model
    def _enrich_normalize_registry(self, value):
        """Normalise an organisation number or VAT number.

        Returns ``(company_registry, vat)`` where ``company_registry`` is ten
        digits without separators and ``vat`` is those digits wrapped as
        ``SE`` … ``01``. Both are ``False`` when ``value`` does not reduce to
        ten digits — we never guess.

        Storage format is deliberately unformatted: ``company_registry`` is
        written and compared in this form, and formatted only for display.
        """
        if not value:
            return False, False
        text = str(value).strip()
        digits = _NON_DIGIT.sub('', text)
        # A VAT number is the organisation number with a two-digit check suffix;
        # the ``SE`` prefix carries no digits, so it is already gone above.
        # Ten digits is the organisation number itself, twelve is orgnr + suffix.
        if len(digits) == 12 and text.upper().startswith('SE'):
            digits = digits[:10]
        if len(digits) != 10:
            return False, False
        return digits, f'SE{digits}01'

    # -- Autocomplete (the widget's data source) ----------------------------

    #: The widget submits one keystroke-bound query per character; a two-letter
    #: query matches half of Sweden and costs a provider call for nothing.
    ENRICH_MIN_QUERY = 3

    @api.model
    def _enrich_query_country(self, query_country_id):
        """Resolve the widget's country argument to a country recordset.

        ``False`` means "use the company's country", ``0`` means "no country
        filter at all" — the widget relies on that distinction to decide
        whether to show the country name in the dropdown.
        """
        if query_country_id is False:
            return self.env.company.country_id
        if query_country_id == 0:
            return self.env['res.country']
        return self.env['res.country'].browse(query_country_id)

    @api.model
    def _enrich_suggestion(self, provider_key, canonical, reference=False):
        """Shape one canonical dict into the widget's suggestion format.

        The widget is strict about this: it reads ``name``, ``city``,
        ``country_id.display_name`` and passes ``duns`` straight back to
        :meth:`enrich_by_duns`. That is why ``duns`` carries our
        ``<provider>:<reference>`` handle rather than a real DUNS number — it is
        the only opaque value the widget will round-trip for us.

        ``reference`` is passed separately, not read from the canonical dict:
        it is transport metadata, not company data, and putting it in the dict
        would mean either widening the contract or having ``clean()`` drop it.
        """
        country_code = canonical.get('country_code')
        country = False
        if country_code:
            country = self.env['res.country'].search(
                [('code', '=', str(country_code).upper())], limit=1,
            )
        return {
            'name': canonical.get('name') or '',
            'city': canonical.get('city') or '',
            'country_id': (
                {'id': country.id, 'display_name': country.display_name}
                if country else False
            ),
            'vat': canonical.get('vat') or '',
            'company_registry': canonical.get('company_registry') or '',
            'duns': '%s:%s' % (provider_key, reference or ''),
        }

    @api.model
    def _enrich_reference(self, canonical):
        """The provider-side id for a canonical result.

        Providers put it in ``raw.payload`` (part of the canonical format) so
        the reference survives :func:`clean` without inventing a private key.
        Falls back to the organisation number, which is the reference most
        providers can look a company up by anyway.
        """
        payload = canonical.get('payload')
        if isinstance(payload, dict):
            reference = pick(payload, 'id', 'reference', 'orgnr', 'company_id')
            if reference:
                return str(reference)
        return canonical.get('company_registry') or ''

    @api.model
    def _enrich_lookup(self, ctx, limit=8):
        """Collect and resolve candidates for the autocomplete dropdown.

        Returns ``[(provider_key, canonical)]``, de-duplicated on the
        organisation number so that two providers describing the same company
        do not produce two identical rows.
        """
        partner_model = self.env['res.partner']
        collected = partner_model._enrich_collect(ctx)
        if not collected:
            return []
        seen = set()
        results = []
        for provider_key, data in collected:
            # A provider that returns a *list* of companies is a search; one
            # that returns a dict is a single-company lookup.
            rows = data if isinstance(data, list) else [data]
            for row in rows:
                if not isinstance(row, dict):
                    continue
                canonical = clean(row)
                if not canonical.get('name'):
                    continue
                key = canonical.get('company_registry') or canonical.get('name')
                if key in seen:
                    continue
                seen.add(key)
                results.append((provider_key, canonical))
                if len(results) >= limit:
                    return results
        return results

    @api.model
    def autocomplete_by_name(self, query, query_country_id, timeout=15):
        """Suggest companies by name, from our own providers.

        Replaces the IAP call. Returns the list shape the widget expects; an
        empty list is a valid answer ("found nothing"), never an error.
        """
        query = (query or '').strip()
        if len(query) < self.ENRICH_MIN_QUERY:
            return []
        country = self._enrich_query_country(query_country_id)
        ctx = {
            'name': query,
            'country_code': country.code if country else False,
            'registry': False,
            'vat': False,
            'website': False,
            'mode': 'search',
            'record': self.env['res.partner'],
        }
        return [
            self._enrich_suggestion(
                provider_key, canonical, self._enrich_reference(canonical),
            )
            for provider_key, canonical in self._enrich_lookup(ctx)
        ]

    @api.model
    def autocomplete_by_vat(self, vat, query_country_id, timeout=15):
        """Suggest companies by VAT number, from our own providers.

        The input is a VAT *fragment* — people type ``556000`` and expect the
        company — so it is normalised to the organisation-number digits and
        matched on prefix, not on equality.
        """
        registry, normalised_vat = self._enrich_normalize_registry(vat)
        digits = registry or re.sub(r'\D', '', str(vat or ''))
        if len(digits) < self.ENRICH_MIN_QUERY:
            return []
        country = self._enrich_query_country(query_country_id)
        ctx = {
            'name': False,
            'registry': digits,
            'vat': normalised_vat,
            'country_code': country.code if country else False,
            'website': False,
            'mode': 'search',
            'record': self.env['res.partner'],
        }
        return [
            self._enrich_suggestion(
                provider_key, canonical, self._enrich_reference(canonical),
            )
            for provider_key, canonical in self._enrich_lookup(ctx)
        ]

    @api.model
    def enrich_by_duns(self, duns, timeout=15):
        """Fetch detail data for one suggestion.

        ``duns`` is our own ``<provider>:<reference>`` handle from
        :meth:`_enrich_suggestion`, not a DUNS number. Returns the
        ``{'data': {...}}`` wrapper the widget's ``getCreateData()``
        destructures; on failure it returns ``{'error': True, ...}`` so the
        widget can show a notification instead of silently doing nothing.

        There is deliberately no ``credit_error`` key: nothing here is billed,
        and answering ``Insufficient Credit`` would send the user to an IAP
        top-up page that has no bearing on our providers.
        """
        if not duns:
            return {'error': True, 'error_message': 'No company reference given.'}
        provider_key, _, reference = str(duns).partition(':')
        if not reference:
            # No provider prefix: a real DUNS number from an imported record.
            return {
                'error': True,
                'error_message': 'No enrichment provider matches %r.' % duns,
            }
        policy = self.env['res.partner.enrich.policy']
        if provider_key not in policy._enrich_provider_keys():
            _logger.info(
                "enrich_by_duns: provider %r is not in the configured order.",
                provider_key,
            )
            return {
                'error': True,
                'error_message': 'Provider %r is not enabled.' % provider_key,
            }
        ctx = {
            'name': False,
            'registry': False,
            'vat': False,
            'country_code': False,
            'website': False,
            'reference': reference,
            'mode': 'detail',
            'record': self.env['res.partner'],
        }
        try:
            data = self.env['res.partner']._enrich_from_provider(provider_key, ctx)
        except Exception:  # noqa: BLE001 - reported to the widget, not raised
            _logger.warning(
                "enrich_by_duns: provider %r failed for reference %r.",
                provider_key, reference, exc_info=True,
            )
            return {
                'error': True,
                'error_message': 'The provider could not be reached.',
            }
        data = clean(data or {})
        if not data:
            return {
                'error': True,
                'error_message': 'No data found for %r.' % reference,
            }
        # Re-shape to the flat dict the widget merges into the form record.
        out = dict(data)
        if data.get('country_code'):
            country = self.env['res.country'].search(
                [('code', '=', str(data['country_code']).upper())], limit=1,
            )
            if country:
                out['country_id'] = {
                    'id': country.id, 'display_name': country.display_name,
                }
        out.pop('country_code', None)
        return {'data': out}

    # -- Enrichment entry point ---------------------------------------------

    @api.model
    def _enrich_from_provider(self, provider_key, ctx):
        """Answer one provider's lookup. Providers override this.

        Defined here, returning nothing, for one reason: without a base
        definition ``super()._enrich_from_provider(...)`` raises
        ``AttributeError`` the moment a second provider module inherits the
        first. Two providers that both override a method nobody declared is a
        module set that cannot be installed together.

        Returning falsy means "this provider has nothing to say", which is a
        normal answer — the dispatcher moves to the next provider.
        """
        return [] if (ctx or {}).get('mode') == 'search' else {}

    def _enrich_collect(self, ctx):
        """Ask every configured provider for data. Returns ``[(key, data)]``.

        ``data`` is whatever the provider returned: a canonical dict for a
        single-company lookup, or a list of dicts for a search. Cleaning is the
        caller's job, because a search result is a list of records to clean
        individually, not one record whose keys are cleaned.

        A provider that raises is logged and skipped, never allowed to abort
        the run: one broken API must not make the other sources useless.
        """
        policy = self.env['res.partner.enrich.policy']
        collected = []
        for provider_key in policy._enrich_provider_keys():
            try:
                data = self._enrich_from_provider(provider_key, ctx)
            except Exception:  # noqa: BLE001 - one provider must not sink the run
                _logger.warning(
                    "Enrichment provider %r failed — continuing with the rest.",
                    provider_key, exc_info=True,
                )
                continue
            if not data:
                _logger.debug(
                    "Enrichment provider %r returned nothing.", provider_key,
                )
                continue
            collected.append((provider_key, data))
        return collected

    def _enrich_current_values(self, data_keys):
        """The values currently stored on this record for ``data_keys``."""
        self.ensure_one()
        wanted = {PARTNER_FIELD_MAP[key] for key in data_keys
                  if key in PARTNER_FIELD_MAP}
        if not wanted:
            return {}
        stored = self.read(list(wanted))[0]
        current = {}
        for key in data_keys:
            fname = PARTNER_FIELD_MAP.get(key)
            if not fname or fname not in stored:
                continue
            value = stored[fname]
            # Many2one is read as (id, display_name); the canonical format
            # compares against the code, so keep only what policy needs to
            # decide "is this field empty".
            if isinstance(value, (list, tuple)):
                value = value[0] if value else False
            current[key] = value
        return current

    def _enrich_prepare_vals(self, resolved):
        """Turn ``{key: (value, provider)}`` into Odoo ``write()`` values."""
        vals = {}
        for key, (value, _provider) in resolved.items():
            fname = PARTNER_FIELD_MAP.get(key)
            if not fname:
                continue
            if fname == 'country_id':
                country = self.env['res.country'].search(
                    [('code', '=', str(value).upper())], limit=1,
                )
                if not country:
                    _logger.info(
                        "Enrichment: unknown country code %r — skipped.", value,
                    )
                    continue
                vals[fname] = country.id
                continue
            vals[fname] = value
        return vals

    def partner_enrich(self):
        """Enrich these contacts from the configured providers.

        Public, argument-free entry point kept from the original API — callers
        in other modules and in server actions depend on the signature.
        """
        policy = self.env['res.partner.enrich.policy']
        for partner in self:
            ctx = partner._enrich_context()
            # ``mode='enrich'``: one detail lookup per provider, not a search.
            collected = [
                (provider_key, clean(data))
                for provider_key, data in partner._enrich_collect(ctx)
                if isinstance(data, dict)
            ]
            collected = [(k, d) for k, d in collected if d]
            if not collected:
                _logger.info(
                    "Enrichment: no provider returned data for %r.",
                    partner.display_name,
                )
                continue

            data_keys = {key for _pkey, data in collected for key in data}
            current = partner._enrich_current_values(data_keys)
            resolved = policy._enrich_resolve(collected, current)
            vals = partner._enrich_prepare_vals(resolved)
            extra = partner._enrich_apply_extra(resolved, collected)

            if not vals and not extra:
                _logger.info(
                    "Enrichment: nothing to write for %r (policy left every "
                    "field alone).", partner.display_name,
                )
                continue

            # One write per record: each write() on a partner triggers the
            # image/address machinery, and a field-by-field loop is both slower
            # and produces a scattered chatter trail.
            provider_keys = sorted({pkey for pkey, _d in collected})
            vals.update(extra or {})
            vals.update({
                'enrich_fetched_at': fields.Datetime.now(),
                'enrich_provider': ','.join(provider_keys),
                'enrich_raw': partner._enrich_raw_payload(collected),
            })
            partner.write(vals)
            partner._enrich_message_post(resolved)
        return True

    # -- Scheduled refresh --------------------------------------------------

    #: How many records the cron touches per batch. Small enough that a slow
    #: provider cannot hold a transaction open for minutes, large enough that
    #: the per-batch overhead does not dominate.
    ENRICH_CRON_BATCH = 100

    @api.model
    def _enrich_refresh_days(self):
        """How stale a record must be before the cron refreshes it.

        Default 365: enrichment data (address, board, financials) changes on
        the order of a year, and re-scraping every partner nightly would be
        both pointless and hostile to the providers.
        """
        raw = self.env['ir.config_parameter'].sudo().get_param(
            'partner_enrich.refresh_days', default='365',
        )
        try:
            days = int(raw)
        except (TypeError, ValueError):
            _logger.warning(
                "partner_enrich.refresh_days is %r, not an integer — using "
                "365.", raw,
            )
            return 365
        return max(days, 0)

    @api.model
    def _enrich_cron_domain(self, days):
        """Records that are due for a refresh.

        Companies only: a private person has no organisation number to look
        up, and trying would burn one provider call per contact.
        """
        domain = [('is_company', '=', True), ('active', '=', True)]
        if days:
            cutoff = fields.Datetime.subtract(
                fields.Datetime.now(), days=days,
            )
            domain += [
                '|',
                ('enrich_fetched_at', '=', False),
                ('enrich_fetched_at', '<', cutoff),
            ]
        return domain

    @api.model
    def _enrich_cron(self, dry_run=False):
        """Refresh stale enrichment data. Returns the number of records.

        ``dry_run`` counts the candidates and writes nothing — the way to find
        out what a nightly job would do before letting it do it.
        """
        days = self._enrich_refresh_days()
        domain = self._enrich_cron_domain(days)
        total = self.search_count(domain)
        _logger.info(
            "Enrichment refresh: %s record(s) due (refresh_days=%s%s).",
            total, days, ', dry run' if dry_run else '',
        )
        if dry_run or not total:
            return total

        processed = 0
        # ``split_every`` chunks an *iterable of ids*; the third argument is a
        # callable that collects each chunk into a recordset. Passing the domain
        # would chunk the domain's tuples, and passing the recordset raises
        # ``TypeError: 'res.partner' object is not callable``.
        ids = self.search(domain).ids
        # Committing per batch is right in a cron and wrong in a test (and in
        # any caller that wants its own transaction). It is therefore opt-in via
        # context rather than unconditional.
        commit_per_batch = self.env.context.get('enrich_commit_per_batch', True)
        for batch in tools.split_every(
            self.ENRICH_CRON_BATCH, ids, self.browse,
        ):
            batch.partner_enrich()
            processed += len(batch)
            if commit_per_batch:
                # A provider that hangs on record 37 must not roll back the 99
                # that already succeeded.
                self.env.cr.commit()  # noqa: SLF001 - deliberate boundary
        _logger.info("Enrichment refresh: processed %s record(s).", processed)
        return processed

    def _enrich_context(self):
        """The lookup context handed to providers.

        ``registry`` is our normalised organisation number and ``vat`` the
        normalised VAT number — providers must never normalise on their own,
        that is what produced three different formats for the same company.
        """
        self.ensure_one()
        registry, vat = self._enrich_normalize_registry(
            self.company_registry or self.vat,
        )
        return {
            'name': self.name,
            'registry': registry,
            'vat': vat,
            'country_code': self.country_id.code or 'SE',
            'website': self.website,
            'duns': self.partner_gid or False,
            'mode': 'enrich',
            'record': self,
        }

    def _enrich_apply_extra(self, resolved, collected):
        """Hook for provider modules to map their own fields.

        The base module may only name fields it owns; ``foretagssok_*``,
        ``bw_*`` and ``mining_*`` are mapped by the modules that define them.

        ``collected`` is the raw ``[(provider_key, canonical)]`` list. It is
        passed explicitly rather than stashed on ``self``: a provider needs the
        *unresolved* payload to reach its own nested data, and threading it
        through the signature is the difference between a hook and a hidden
        global.
        """
        return {}

    def _enrich_raw_payload(self, collected):
        """The provider responses as JSON, for troubleshooting and re-apply."""
        payload = {}
        for provider_key, data in collected:
            serialisable = {}
            for key, value in data.items():
                try:
                    json.dumps(value)
                except (TypeError, ValueError):
                    serialisable[key] = str(value)
                else:
                    serialisable[key] = value
            payload[provider_key] = serialisable
        return json.dumps(payload, ensure_ascii=False, indent=1, default=str)

    def _enrich_message_post(self, resolved):
        """Log the enrichment on the record, one line per field group."""
        self.ensure_one()
        if not hasattr(self, 'message_post'):
            return
        by_provider = {}
        for key, (_value, provider_key) in resolved.items():
            by_provider.setdefault(provider_key, []).append(key)
        if not by_provider:
            return
        lines = [
            '%s: %s' % (provider_key, ', '.join(sorted(keys)))
            for provider_key, keys in sorted(by_provider.items())
        ]
        self.message_post(
            body='Company data refreshed.<br/>' + '<br/>'.join(lines),
            subtype_xmlid='mail.mt_note',
        )

    @api.model
    def orgnr2vat(self, company_registry):
        """Backwards-compatible wrapper — delegates to the normaliser."""
        return self._enrich_normalize_registry(company_registry)[1] or None

    def enrich_company(self, company_domain, partner_gid, vat,
                       timeout=COMPANY_AC_TIMEOUT):  # Override IAP-version
        res = {}
        if COMPANY_NO_IAP:
            res = super().enrich_company(company_domain, partner_gid, vat)
        return res
