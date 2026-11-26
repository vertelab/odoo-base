# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase

from odoo.addons.partner_enrich_base.models.enrich_format import (
    FIELD_GROUP,
    clean,
)


def _set_param(params, key, value):
    """set_param on 18/19, set_str on 20 (renamed)."""
    setter = getattr(params, 'set_str', None) or params.set_param
    return setter(key, value)

#: A FöretagsAPI company object, shaped like the real response.
COMPANY = {
    'name': 'Testbolaget AB',
    'orgNumber': '556000-1234',
    'legalForm': 'Aktiebolag',
    'registrationDate': '1990-03-12',
    'businessDescription': 'Konsultverksamhet inom IT.',
    'postalAddress': {
        'street': 'Storgatan 1',
        'postalCode': '111 22',
        'city': 'Stockholm',
    },
    'sniCodes': {
        'sni1': '62020',
        'sni1_name': 'Dataprogrammering',
        'sni2': '70220',
        'sni2_name': 'Företagsrådgivning',
        'sni3': '00000',
    },
    'financials': {
        'year': 2024,
        'revenue': 12500000.0,
        'operatingResult': 1500000.0,
        'netResult': 1200000.0,
        'totalAssets': 8000000.0,
        'equity': 3000000.0,
        'employees': 12,
        'currency': 'SEK',
        'taxonomy': 'K2',
        'fiscalYearStart': '2024-01-01',
        'fiscalYearEnd': '2024-12-31',
    },
    'revenue_estimate': {'type': 'exact', 'value': 12500000, 'reference_year': '2024'},
    'employees_estimate': {'type': 'exact', 'value': 12, 'reference_year': '2024'},
}


class ForetagsapiMappingCase(TransactionCase):

    def setUp(self):
        super().setUp()
        self.partner_model = self.env['res.partner']

    def _map(self, company=None):
        return self.partner_model._foretagsapi_map_company(
            company if company is not None else COMPANY,
        )


class TestCanonicalMapping(ForetagsapiMappingCase):

    def test_only_canonical_keys_are_returned(self):
        """A provider that emits a non-canonical key trips a base warning."""
        canonical = self._map()
        unknown = set(canonical) - set(FIELD_GROUP)
        self.assertEqual(
            unknown, set(),
            'Provider returned keys outside the contract: %s' % unknown,
        )

    def test_clean_does_not_warn_on_the_mapping(self):
        """``clean()`` must accept the mapping as-is — no dropped keys."""
        canonical = self._map()
        with self.assertNoLogs(
            'odoo.addons.partner_enrich_base.models.enrich_format', level='WARNING',
        ):
            cleaned = clean(canonical)
        self.assertEqual(set(cleaned), set(clean(canonical)))

    def test_organisation_number_is_passed_through_raw(self):
        """Normalisation is the base module's job, not the provider's."""
        canonical = self._map()
        self.assertEqual(canonical['company_registry'], '556000-1234')

    def test_identity_fields(self):
        canonical = self._map()
        self.assertEqual(canonical['name'], 'Testbolaget AB')
        self.assertEqual(canonical['legal_form'], 'Aktiebolag')
        self.assertEqual(str(canonical['registration_date']), '1990-03-12')
        self.assertEqual(canonical['status'], 'Active')

    def test_address(self):
        canonical = self._map()
        self.assertEqual(canonical['street'], 'Storgatan 1')
        self.assertEqual(canonical['zip'], '111 22')
        self.assertEqual(canonical['city'], 'Stockholm')
        self.assertEqual(canonical['country_code'], 'SE')

    def test_sni_codes_skip_the_placeholder(self):
        canonical = self._map()
        self.assertEqual(canonical['sni_codes'], ['62020', '70220'])

    def test_financials_are_canonical_entries(self):
        canonical = self._map()
        self.assertEqual(len(canonical['financials']), 1)
        entry = canonical['financials'][0]
        self.assertEqual(entry['fiscal_year'], '2024')
        self.assertEqual(entry['net_sales'], 12500000.0)
        self.assertEqual(entry['employees'], 12)
        self.assertEqual(entry['currency'], 'SEK')

    def test_zero_financial_figure_survives(self):
        """A zero result is data, not emptiness."""
        company = dict(COMPANY, financials=dict(COMPANY['financials'], netResult=0))
        canonical = self._map(company)
        self.assertEqual(canonical['financials'][0]['net_result'], 0.0)

    def test_empty_company_gives_empty_dict(self):
        self.assertEqual(self._map({}), {})

    def test_raw_payload_is_carried_for_the_detail_call(self):
        canonical = self._map()
        self.assertEqual(canonical['payload']['orgNumber'], '556000-1234')


class TestEstimates(ForetagsapiMappingCase):

    def test_estimates_are_not_canonical(self):
        """They are provider fields, so they must not enter the canonical dict."""
        canonical = self._map()
        self.assertNotIn('foretagssok_revenue_estimate', canonical)

    def test_negative_placeholder_is_dropped(self):
        estimates = self.partner_model._foretagsapi_map_estimates({
            'revenue_estimate': {'type': 'exact', 'value': -1, 'reference_year': '2024'},
            'employees_estimate': {'type': 'exact', 'value': 12, 'reference_year': '2024'},
        })
        self.assertFalse(estimates['foretagssok_revenue_estimate'])
        self.assertEqual(estimates['foretagssok_employees_estimate'], 12)
        self.assertEqual(estimates['foretagssok_estimates_reference_year'], '2024')

    def test_none_type_is_dropped(self):
        estimates = self.partner_model._foretagsapi_map_estimates({
            'revenue_estimate': {'type': 'none'},
            'employees_estimate': {'type': 'none'},
        })
        self.assertFalse(estimates['foretagssok_revenue_estimate'])
        self.assertFalse(estimates['foretagssok_employees_estimate'])


class TestProviderContract(ForetagsapiMappingCase):

    def test_unknown_provider_key_is_declined(self):
        """Another provider's key must fall through to ``super()``."""
        result = self.partner_model._enrich_from_provider(
            'allabolag', {'mode': 'search', 'name': 'Test'},
        )
        self.assertFalse(result)

    def test_missing_api_key_does_not_raise(self):
        """An unconfigured provider must not drown the log on every run."""
        _set_param(
            self.env['ir.config_parameter'].sudo(),
            'partner_foretagssok.api_key', '',
        )
        result = self.partner_model._enrich_from_provider(
            'foretagssok', {'mode': 'enrich', 'name': 'Testbolaget'},
        )
        self.assertEqual(result, {})

    def test_missing_api_key_gives_empty_list_in_search_mode(self):
        result = self.partner_model._enrich_from_provider(
            'foretagssok', {'mode': 'search', 'name': 'Testbolaget'},
        )
        self.assertEqual(result, [])

    def test_missing_api_key_makes_no_http_request(self):
        """The failure must be local: no key, no call, no leaked request.

        Asserting only that it returns empty would pass just as well if we
        called the API with an empty Bearer token — and that is a request that
        leaks the endpoint and burns rate limit for nothing.
        """
        import os
        from unittest.mock import patch

        previous = os.environ.get('ENRICH_ENV_FILE')
        os.environ['ENRICH_ENV_FILE'] = '/nonexistent/enrich.env'
        try:
            with patch(
                'odoo.addons.partner_foretagssok.models.res_partner.requests.post',
            ) as post:
                self.partner_model._enrich_from_provider(
                    'foretagssok',
                    {'mode': 'enrich', 'name': 'Testbolaget', 'registry': False},
                )
                post.assert_not_called()
        finally:
            if previous is None:
                os.environ.pop('ENRICH_ENV_FILE', None)
            else:
                os.environ['ENRICH_ENV_FILE'] = previous

    def test_ensure_config_names_the_setting(self):
        """The error must tell the operator where to put the key."""
        import os

        from odoo.exceptions import UserError

        previous = os.environ.get('ENRICH_ENV_FILE')
        os.environ['ENRICH_ENV_FILE'] = '/nonexistent/enrich.env'
        try:
            with self.assertRaises(UserError) as caught:
                self.partner_model._foretagsapi_ensure_config()
            message = str(caught.exception)
            self.assertIn('keykeep', message)
            self.assertIn('/etc/odoo/enrich.env', message)
        finally:
            if previous is None:
                os.environ.pop('ENRICH_ENV_FILE', None)
            else:
                os.environ['ENRICH_ENV_FILE'] = previous


class TestFinancialCommands(ForetagsapiMappingCase):

    def test_inserts_when_no_row_exists(self):
        partner = self.env['res.partner'].create({'name': 'Test'})
        commands = partner._foretagsapi_financial_commands([
            {'fiscal_year': '2024', 'net_sales': 100.0},
        ])
        self.assertEqual(commands[0][0], 0)

    def test_updates_the_existing_row_for_the_same_year(self):
        """Re-running enrichment must not double-count a fiscal year."""
        partner = self.env['res.partner'].create({'name': 'Test'})
        partner.write({'foretagssok_financial_ids': [(0, 0, {
            'fiscal_year': '2024', 'net_sales': 100.0,
        })]})
        commands = partner._foretagsapi_financial_commands([
            {'fiscal_year': '2024', 'net_sales': 200.0},
        ])
        self.assertEqual(commands[0][0], 1)
        self.assertEqual(commands[0][2]['net_sales'], 200.0)


class TestSecretHandling(ForetagsapiMappingCase):

    def test_api_key_is_not_a_settings_field(self):
        """The credential must not be writable through settings."""
        field = self.env['res.config.settings']._fields.get(
            'foretagssok_api_key')
        self.assertIsNone(
            field,
            'The API key must not be a settings field — it belongs in keykeep.',
        )

    def test_env_file_is_read(self):
        import os
        import tempfile

        handle, path = tempfile.mkstemp()
        os.close(handle)
        with open(path, 'w', encoding='utf-8') as stream:
            stream.write('# comment\nFORETAGSSOK_API_KEY=abc123\n')
        previous = os.environ.get('ENRICH_ENV_FILE')
        os.environ['ENRICH_ENV_FILE'] = path
        try:
            self.assertEqual(
                self.partner_model._foretagsapi_secret_from_env(), 'abc123',
            )
        finally:
            if previous is None:
                os.environ.pop('ENRICH_ENV_FILE', None)
            else:
                os.environ['ENRICH_ENV_FILE'] = previous
            os.unlink(path)

    def test_missing_env_file_is_not_an_error(self):
        import os

        previous = os.environ.get('ENRICH_ENV_FILE')
        os.environ['ENRICH_ENV_FILE'] = '/nonexistent/enrich.env'
        try:
            self.assertFalse(self.partner_model._foretagsapi_secret_from_env())
        finally:
            if previous is None:
                os.environ.pop('ENRICH_ENV_FILE', None)
            else:
                os.environ['ENRICH_ENV_FILE'] = previous
