# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest.mock import patch

from odoo.tests.common import TransactionCase

from odoo.addons.partner_enrich_base.models.enrich_format import (
    FIELD_GROUP,
    clean,
)

#: A ``Company.data`` payload, shaped like the allabolag package returns it.
DATA = {
    'company': {
        'name': 'Testbolaget AB',
        'orgnr': '556000-1234',
        'legalForm': 'Aktiebolag',
        'registrationDate': '1990-03-12',
        'purpose': 'Konsultverksamhet inom IT.',
        'status': {'status': 'Aktiv'},
        'postalAddress': {
            'addressLine': 'Storgatan 1',
            'zipCode': '111 22',
            'postPlace': 'Stockholm',
        },
        'phone': '08-123456',
        'email': 'info@testbolaget.se',
        'homePage': 'https://testbolaget.se',
        'revenue': 12500000,
        'profit': 1500000,
        'employees': 12,
        'accountFiguresYear': 2024,
        'sniCode': '62020',
        'contactPerson': {'name': 'Anna Andersson', 'role': 'VD'},
    },
}


class AllabolagCase(TransactionCase):

    def setUp(self):
        super().setUp()
        self.partner_model = self.env['res.partner']

    def _map(self, data=None):
        return self.partner_model._allabolag_map_company(
            data if data is not None else DATA,
        )


class TestCanonicalMapping(AllabolagCase):

    def test_only_canonical_keys(self):
        canonical = self._map()
        unknown = set(canonical) - set(FIELD_GROUP)
        self.assertEqual(unknown, set(), 'Non-canonical keys: %s' % unknown)

    def test_clean_accepts_the_mapping(self):
        with self.assertNoLogs(
            'odoo.addons.partner_enrich_base.models.enrich_format',
            level='WARNING',
        ):
            clean(self._map())

    def test_organisation_number_is_raw(self):
        self.assertEqual(self._map()['company_registry'], '556000-1234')

    def test_identity(self):
        canonical = self._map()
        self.assertEqual(canonical['name'], 'Testbolaget AB')
        self.assertEqual(canonical['legal_form'], 'Aktiebolag')
        self.assertEqual(canonical['status'], 'Aktiv')
        self.assertEqual(str(canonical['registration_date']), '1990-03-12')

    def test_address_uses_allabolag_key_names(self):
        """``postPlace``/``addressLine``/``zipCode``, not ``city``/``street``."""
        canonical = self._map()
        self.assertEqual(canonical['street'], 'Storgatan 1')
        self.assertEqual(canonical['zip'], '111 22')
        self.assertEqual(canonical['city'], 'Stockholm')
        self.assertEqual(canonical['country_code'], 'SE')

    def test_contact(self):
        canonical = self._map()
        self.assertEqual(canonical['phone'], '08-123456')
        self.assertEqual(canonical['email'], 'info@testbolaget.se')
        self.assertEqual(canonical['website'], 'https://testbolaget.se')

    def test_contact_person_does_not_become_the_name(self):
        """A human's name must never overwrite the company name."""
        canonical = self._map()
        self.assertEqual(canonical['name'], 'Testbolaget AB')
        self.assertEqual(canonical['payload']['_contact']['name'], 'Anna Andersson')

    def test_sni_codes(self):
        self.assertEqual(self._map()['sni_codes'], ['62020'])

    def test_financials(self):
        entry = self._map()['financials'][0]
        self.assertEqual(entry['net_sales'], 12500000.0)
        self.assertEqual(entry['operating_profit'], 1500000.0)
        self.assertEqual(entry['employees'], 12)
        self.assertEqual(entry['fiscal_year'], '2024')

    def test_zero_figure_survives(self):
        data = {'company': dict(DATA['company'], profit=0)}
        self.assertEqual(self._map(data)['financials'][0]['operating_profit'], 0.0)

    def test_financials_without_year_have_no_fiscal_year(self):
        """A guessed year is worse than no year."""
        company = {k: v for k, v in DATA['company'].items()
                   if k != 'accountFiguresYear'}
        entry = self._map({'company': company})['financials'][0]
        self.assertNotIn('fiscal_year', entry)

    def test_empty_data_gives_empty_dict(self):
        self.assertEqual(self._map({}), {})
        self.assertEqual(self._map({'company': {}}), {})


class TestProviderContract(AllabolagCase):

    def test_other_provider_key_falls_through(self):
        result = self.partner_model._enrich_from_provider(
            'foretagssok', {'mode': 'search', 'name': 'X'},
        )
        self.assertFalse(result)

    def test_scrape_failure_returns_empty_not_raise(self):
        """A 403 or a layout change must not abort the whole enrichment run."""
        with patch.object(
            type(self.partner_model), '_allabolag_fetch',
            side_effect=RuntimeError('403 Forbidden'),
        ):
            self.assertEqual(
                self.partner_model._enrich_from_provider(
                    'allabolag', {'mode': 'search', 'registry': '5560001234'},
                ),
                [],
            )
            self.assertEqual(
                self.partner_model._enrich_from_provider(
                    'allabolag', {'mode': 'enrich', 'registry': '5560001234'},
                ),
                {},
            )

    def test_missing_package_is_not_fatal(self):
        with patch.dict('sys.modules', {'allabolag': None}):
            result = self.partner_model._enrich_from_provider(
                'allabolag', {'mode': 'enrich', 'registry': '5560001234'},
            )
        self.assertEqual(result, {})

    def test_fetch_rejects_short_numbers_without_network(self):
        """A five-digit reference is rejected locally, before any request."""
        with patch(
            'odoo.addons.partner_allabolag.models.res_partner.ResPartner'
            '._allabolag_fetch',
            return_value={},
        ) as fetch:
            result = self.partner_model._enrich_from_provider(
                'allabolag', {'mode': 'enrich', 'registry': '12345'},
            )
        self.assertEqual(result, {})
        fetch.assert_called_once_with('12345')

        # And the real guard: calling it directly returns nothing rather than
        # raising or hitting the network.
        with patch(
            'allabolag.Company',
        ) as company:
            self.assertEqual(self.partner_model._allabolag_fetch('12345'), {})
            company.assert_not_called()

    def test_detail_uses_the_reference(self):
        with patch.object(
            type(self.partner_model), '_allabolag_fetch',
            return_value={'name': 'Testbolaget AB'},
        ) as fetch:
            result = self.partner_model._enrich_from_provider(
                'allabolag', {'mode': 'detail', 'reference': '5560001234'},
            )
        self.assertEqual(result['name'], 'Testbolaget AB')
        fetch.assert_called_once_with('5560001234')


class TestExtraFields(AllabolagCase):

    def test_extra_fields_are_applied_when_allabolag_wins(self):
        partner = self.env['res.partner'].create({'name': 'Test'})
        collected = [
            ('allabolag', self._map()),
        ]
        resolved = {'name': ('Testbolaget AB', 'allabolag')}
        vals = partner._enrich_apply_extra(resolved, collected)
        self.assertEqual(vals['summary_revenue'], 12500000.0)
        self.assertEqual(vals['summary_profit_ebit'], 1500000.0)
        self.assertEqual(vals['kpi_no_employees'], 12)
        self.assertEqual(vals['summary_purpose'], 'Konsultverksamhet inom IT.')
        self.assertEqual(vals['contact_name'], 'Anna Andersson')
        self.assertEqual(vals['function'], 'VD')

    def test_extra_fields_are_skipped_when_allabolag_loses(self):
        """A losing provider must not write its own fields."""
        partner = self.env['res.partner'].create({'name': 'Test'})
        collected = [('allabolag', self._map())]
        resolved = {'name': ('Testbolaget AB', 'foretagssok')}
        vals = partner._enrich_apply_extra(resolved, collected)
        self.assertNotIn('summary_revenue', vals)

    def test_employee_estimate_is_derived_from_revenue(self):
        partner = self.env['res.partner'].create({'name': 'Test'})
        company = dict(DATA['company'], employees=0)
        collected = [('allabolag', self._map({'company': company}))]
        vals = partner._enrich_apply_extra(
            {'name': ('X', 'allabolag')}, collected,
        )
        self.assertGreater(vals['kpi_no_employees'], 0)
        self.assertEqual(vals['kpi_no_employees'], int(12500000 // 200000))
