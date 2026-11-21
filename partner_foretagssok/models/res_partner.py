# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import re

import requests

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from odoo.addons.partner_enrich_base.models.enrich_format import empty, pick

from .foretagsapi_mapping import ForetagsapiMappingMixin

_logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = 'https://data.foretagsapi.se'

#: The key this provider registers under in ``partner_enrich.provider_order``.
PROVIDER_KEY = 'foretagssok'


class ResPartner(models.Model, ForetagsapiMappingMixin):
    _inherit = 'res.partner'

    foretagssok_business_description = fields.Text(string='Business Description')
    foretagssok_registration_date = fields.Date(string='Registration Date')
    foretagssok_deregistration_date = fields.Date(string='Deregistration Date')
    foretagssok_status = fields.Char(string='Company Status')
    foretagssok_revenue_estimate = fields.Float(string='Revenue Estimate')
    foretagssok_employees_estimate = fields.Integer(string='Employees Estimate')
    foretagssok_estimates_reference_year = fields.Char(string='Estimates Reference Year')
    foretagssok_financial_ids = fields.One2many(
        'res.partner.financials',
        'partner_id',
        string='Financials',
    )

    # -------------------------------------------------------------------------
    # Configuration
    # -------------------------------------------------------------------------

    @api.model
    def _foretagsapi_get_config(self):
<<<<<<< HEAD
        """Return ``(api_key, base_url)``.

        The API key is an application secret and lives in keykeep, pushed to
        ``/etc/odoo/enrich.env`` by maintenance-runner. It is deliberately not
        read from ``ir.config_parameter``: a credential in a system parameter
        is readable by anyone who can read settings, and it ends up in every
        database dump.
        """
        base_url = self.env['ir.config_parameter'].sudo().get_param(
=======
        params = self.env['ir.config_parameter'].sudo()
        api_key = params.get_str('partner_foretagssok.api_key', default='').strip()
        base_url = params.get_str(
>>>>>>> origin/20.0
            'partner_foretagssok.base_url',
            default=DEFAULT_BASE_URL,
        ).strip().rstrip('/')
        return self._foretagsapi_read_secret(), base_url

    @api.model
    def _foretagsapi_read_secret(self):
        """Read the API key from keykeep, falling back to the env file.

        Two paths on purpose: keykeep is the system of record, but an
        installation that has not been migrated yet still has the key in
        ``/etc/odoo/enrich.env``. Reading both means the migration can be done
        without a window where enrichment silently stops working.
        """
        key = self._foretagsapi_secret_from_keykeep()
        if key:
            return key
        return self._foretagsapi_secret_from_env()

    @api.model
    def _foretagsapi_secret_from_keykeep(self):
        """Look the key up in keykeep by provider key, if keykeep is present."""
        if 'keykeep.credential' not in self.env:
            return False
        credential = self.env['keykeep.credential'].sudo().search([
            ('purpose', '=', PROVIDER_KEY),
            ('credential_type', '=', 'api_key'),
        ], limit=1)
        if not credential:
            return False
        try:
            # system=True writes an audit entry — that is the point of keykeep.
            return credential._read_encrypted('key_value', system=True) or False
        except Exception:  # noqa: BLE001 - a broken key must not break lookup
            _logger.warning(
                "Could not decrypt the FöretagsAPI key from keykeep — falling "
                "back to the environment file.", exc_info=True,
            )
            return False

    @api.model
    def _foretagsapi_secret_from_env(self):
        """Read ``FORETAGSSOK_API_KEY`` from ``/etc/odoo/enrich.env``."""
        import os

        path = os.environ.get(
            'ENRICH_ENV_FILE', '/etc/odoo/enrich.env',
        )
        if not os.path.exists(path):
            return False
        try:
            with open(path, 'r', encoding='utf-8') as handle:
                for line in handle:
                    line = line.strip()
                    if not line or line.startswith('#') or '=' not in line:
                        continue
                    key, value = line.split('=', 1)
                    if key.strip() == 'FORETAGSSOK_API_KEY':
                        return value.strip().strip('"').strip("'") or False
        except OSError:
            _logger.warning("Could not read %s.", path, exc_info=True)
        return False

    @api.model
    def _foretagsapi_ensure_config(self):
        api_key, base_url = self._foretagsapi_get_config()
        if not api_key:
            raise UserError(_(
                'FöretagsAPI API key is missing. Add it as a keykeep credential '
                'with purpose "%s", or set FORETAGSSOK_API_KEY in %s.'
            ) % (PROVIDER_KEY, '/etc/odoo/enrich.env'))
        return api_key, base_url

    @api.model
    def _foretagsapi_migrate_secret(self, api_key):
        """Move a legacy ``ir.config_parameter`` key to the environment file.

        Called from ``post_init_hook``. Writes ``/etc/odoo/enrich.env`` with
        ``0600`` — the file is read by the Odoo process and by nothing else.
        """
        import os
        import stat

        path = os.environ.get('ENRICH_ENV_FILE', '/etc/odoo/enrich.env')
        lines = []
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as handle:
                    lines = [
                        line for line in handle.read().splitlines()
                        if not line.strip().startswith('FORETAGSSOK_API_KEY=')
                    ]
            except OSError:
                _logger.warning(
                    "Could not read %s while migrating the API key.",
                    path, exc_info=True,
                )
                return False
        lines.append('FORETAGSSOK_API_KEY=%s' % api_key)
        try:
            directory = os.path.dirname(path)
            if directory and not os.path.isdir(directory):
                os.makedirs(directory, mode=0o750, exist_ok=True)
            descriptor = os.open(
                path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600,
            )
            with os.fdopen(descriptor, 'w', encoding='utf-8') as handle:
                handle.write('\n'.join(lines) + '\n')
            os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)
        except OSError:
            _logger.warning(
                "Could not write %s while migrating the API key. The key is "
                "still in ir.config_parameter.", path, exc_info=True,
            )
            return False
        _logger.info("FöretagsAPI API key moved to %s.", path)
        return True

    # -------------------------------------------------------------------------
    # API client
    # -------------------------------------------------------------------------

    @api.model
    def _foretagsapi_request(self, endpoint, payload):
        api_key, base_url = self._foretagsapi_ensure_config()
        response = requests.post(
            '%s%s' % (base_url, endpoint),
            json=payload,
            headers={
                'Authorization': 'Bearer %s' % api_key,
                'Content-Type': 'application/json',
            },
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    @api.model
    def _foretagsapi_search_by_name(self, name, limit=5):
        if empty(name):
            return []
        result = self._foretagsapi_request(
            '/v1/search', {'q': name, 'limit': limit},
        )
        return result.get('companies', [])

    @api.model
    def _foretagsapi_lookup_by_org_numbers(self, org_numbers):
        """Look up one or many organisation numbers via the bulk endpoint."""
        digits = [
            re.sub(r'\D', '', str(number))
            for number in org_numbers or [] if number
        ]
        digits = [d for d in digits if len(d) == 10]
        if not digits:
            return []
        result = self._foretagsapi_request('/v1/bulk', {'org_numbers': digits})
        return [
            item.get('company')
            for item in result.get('results', [])
            if item.get('success') and item.get('company')
        ]

    @api.model
    def _foretagsapi_search_by_sni(
        self,
        sni_code,
        city=None,
        min_revenue=None,
        max_revenue=None,
        has_annual_report=None,
        exact_only=None,
        sort_by=None,
        limit=100,
        offset=0,
    ):
        if not sni_code:
            return []
        payload = {'sni_code': sni_code, 'limit': limit, 'offset': offset}
        if city:
            payload['city'] = city
        if min_revenue is not None:
            payload['minRevenue'] = min_revenue
        if max_revenue is not None:
            payload['maxRevenue'] = max_revenue
        if has_annual_report is not None:
            payload['hasAnnualReport'] = has_annual_report
        if exact_only is not None:
            payload['exactOnly'] = exact_only
        if sort_by:
            payload['sort'] = sort_by
        result = self._foretagsapi_request('/v1/sni/search', payload)
        return result.get('companies', [])

    # -------------------------------------------------------------------------
    # Provider contract
    # -------------------------------------------------------------------------

    @api.model
    def _enrich_from_provider(self, provider_key, ctx):
        """Answer the base module's provider call for ``foretagssok``.

        Three modes:

        ``search``  — return a list of canonical dicts for the dropdown.
        ``detail``  — return one canonical dict for a chosen suggestion.
        ``enrich``  — return one canonical dict for a specific record.

        Returning ``[]``/``{}`` means "found nothing", which is an answer, not
        an error. Raising means "the provider is broken" and the base module
        logs it and moves on — so a missing API key must not raise here, or one
        unconfigured provider would drown the log on every run.
        """
        if provider_key != PROVIDER_KEY:
            return super()._enrich_from_provider(provider_key, ctx)
        mode = ctx.get('mode') or 'enrich'
        try:
            if mode == 'search':
                return self._foretagsapi_search(ctx)
            if mode == 'detail':
                return self._foretagsapi_detail(ctx)
            return self._foretagsapi_enrich(ctx)
        except UserError as error:
            # Configuration problems are not provider failures — report them
            # once, at info level, and return "nothing found".
            _logger.info("FöretagsAPI not usable: %s", error)
            return [] if mode == 'search' else {}

    @api.model
    def _foretagsapi_search(self, ctx):
        """Search by name and/or organisation number, deduplicated."""
        registry = ctx.get('registry')
        name = ctx.get('name')
        companies = []
        if registry:
            companies = self._foretagsapi_lookup_by_org_numbers([registry])
        if not companies and name:
            companies = self._foretagsapi_search_by_name(name, limit=8)
        return [
            self._foretagsapi_map_company(company)
            for company in companies
            if company
        ]

    @api.model
    def _foretagsapi_detail(self, ctx):
        """One company, by the reference the dropdown handed back."""
        reference = ctx.get('reference')
        if empty(reference):
            return {}
        companies = self._foretagsapi_lookup_by_org_numbers([reference])
        if not companies:
            return {}
        return self._foretagsapi_map_company(companies[0])

    @api.model
    def _foretagsapi_enrich(self, ctx):
        """One company for a specific record.

        Prefers the organisation number; falls back to name only when the name
        is unambiguous. Guessing between several matches is how a partner ends
        up enriched with a stranger's address.
        """
        registry = ctx.get('registry')
        companies = []
        if registry:
            companies = self._foretagsapi_lookup_by_org_numbers([registry])
        if not companies:
            name = ctx.get('name')
            if empty(name):
                return {}
            companies = self._foretagsapi_search_by_name(name, limit=5)
            if len(companies) > 1:
                _logger.info(
                    "FöretagsAPI found %s matches for %r — not guessing.",
                    len(companies), name,
                )
                return {}
        if not companies:
            return {}
        return self._foretagsapi_map_company(companies[0])

    # -------------------------------------------------------------------------
    # Provider-specific fields
    # -------------------------------------------------------------------------

    def _enrich_apply_extra(self, resolved, collected):
        """Map ``foretagssok_*`` fields and the financials one2many.

        Called by ``partner_enrich_base`` after the policy has resolved the
        canonical keys. Only applied when this provider actually won a field
        group — otherwise a losing provider would still write its own fields.
        """
        vals = super()._enrich_apply_extra(resolved, collected)
        if not any(pkey == PROVIDER_KEY for _v, pkey in resolved.values()):
            return vals
        canonical = dict(collected).get(PROVIDER_KEY) or {}
        company = canonical.get('payload') or {}
        if not company:
            return vals

        estimates = self._foretagsapi_map_estimates(company)
        for key, value in estimates.items():
            if not empty(value):
                vals[key] = value

        description = pick(company, 'businessDescription')
        if description:
            vals['foretagssok_business_description'] = description
        deregistration = self._foretagsapi_parse_date(
            company.get('deregistrationDate'))
        if deregistration:
            vals['foretagssok_deregistration_date'] = deregistration

        financials = self._foretagsapi_map_financials(company)
        if financials:
            vals['foretagssok_financial_ids'] = (
                self._foretagsapi_financial_commands(financials)
            )
        return vals

    def _foretagsapi_financial_commands(self, financials):
        """Replace the current fiscal year's row instead of duplicating it.

        A one2many ``(0, 0, vals)`` command appends; running enrichment twice
        would otherwise leave two rows for the same year and every financial
        report would double-count.
        """
        self.ensure_one()
        commands = []
        for entry in financials:
            fiscal_year = entry.get('fiscal_year')
            existing = self.foretagssok_financial_ids.filtered(
                lambda row: row.fiscal_year == fiscal_year
            ) if fiscal_year else self.foretagssok_financial_ids
            if existing:
                commands.append((1, existing[0].id, entry))
                for extra in existing[1:]:
                    commands.append((2, extra.id, 0))
            else:
                commands.append((0, 0, entry))
        return commands

    # -------------------------------------------------------------------------
    # Actions
    # -------------------------------------------------------------------------

    def action_foretagsapi_enrich(self):
        self.partner_enrich()

    def action_foretagsapi_find_similar(self):
        self.ensure_one()
        if not self.sni_id:
            raise UserError(_('This company has no SNI code to search from.'))
        return {
            'type': 'ir.actions.act_window',
            'name': _('Companies with SNI %s') % self.sni_id.code,
            'res_model': 'foretagssok.similar.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_partner_id': self.id,
                'default_sni_code': self.sni_id.code,
                'default_sni_name': self.sni_id.name,
            },
        }
