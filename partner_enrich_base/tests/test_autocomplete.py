# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class AutocompleteCase(TransactionCase):
    """Fake provider plumbing for the widget-facing methods."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_model = cls.env['res.partner']
        cls.params = cls.env['ir.config_parameter'].sudo()
        cls.params.set_param('partner_enrich.provider_order', 'foretagssok,allabolag')

    def _install_provider(self, handler):
        """Install ``handler(provider_key, ctx)`` as the provider callable."""
        partner_model = type(self.partner_model)

        def _call(self, provider_key, ctx):
            return handler(provider_key, ctx)

        partner_model._enrich_from_provider = _call
        self.addCleanup(lambda: delattr(partner_model, '_enrich_from_provider'))


class TestAutocompleteByVat(AutocompleteCase):

    def test_vat_and_name_are_normalised_to_the_same_digits(self):
        """``test_vat_input``/``test_spaced_vat_input`` shape, through the widget.

        The bug being prevented: ``SE556000123401`` used to lose its first two
        digits because the ``SE`` prefix was stripped off the digit string.
        """
        seen = {}

        def handler(provider_key, ctx):
            seen[provider_key] = dict(ctx)
            return [{'name': 'Testbolaget AB', 'company_registry': '5560001234'}]

        self._install_provider(handler)
        self.partner_model.autocomplete_by_vat('SE556000123401', False)
        self.assertEqual(seen['foretagssok']['registry'], '5560001234')
        self.assertEqual(seen['foretagssok']['vat'], 'SE556000123401')

    def test_spaced_vat_normalises(self):
        seen = {}

        def handler(provider_key, ctx):
            seen[provider_key] = dict(ctx)
            return []

        self._install_provider(handler)
        self.partner_model.autocomplete_by_vat('SE 556000 1234 01', False)
        self.assertEqual(seen['foretagssok']['registry'], '5560001234')

    def test_partial_digits_are_accepted(self):
        """People type ``556000`` and expect the company, not nothing."""
        seen = {}

        def handler(provider_key, ctx):
            seen[provider_key] = dict(ctx)
            return [{'name': 'Testbolaget AB'}]

        self._install_provider(handler)
        result = self.partner_model.autocomplete_by_vat('556000', False)
        self.assertEqual(seen['foretagssok']['registry'], '556000')
        self.assertEqual(len(result), 1)

    def test_too_short_query_returns_empty_without_calling_provider(self):
        calls = []

        def handler(provider_key, ctx):
            calls.append(provider_key)
            return [{'name': 'Should not appear'}]

        self._install_provider(handler)
        self.assertEqual(self.partner_model.autocomplete_by_vat('55', False), [])
        self.assertEqual(calls, [])

    def test_empty_input_returns_empty(self):
        self._install_provider(lambda key, ctx: [{'name': 'X'}])
        self.assertEqual(self.partner_model.autocomplete_by_vat(False, False), [])


class TestAutocompleteByName(AutocompleteCase):

    def test_suggestion_shape_matches_the_widget(self):
        """The widget reads name/city/country_id/duns — all must be present."""
        self._install_provider(lambda key, ctx: [{
            'name': 'Testbolaget AB',
            'city': 'Stockholm',
            'country_code': 'SE',
            'vat': 'SE556000123401',
            'company_registry': '5560001234',
            'payload': {'id': 'abc123'},
        }])
        result = self.partner_model.autocomplete_by_name('Testbolaget', False)
        self.assertEqual(len(result), 1)
        suggestion = result[0]
        self.assertEqual(suggestion['name'], 'Testbolaget AB')
        self.assertEqual(suggestion['city'], 'Stockholm')
        self.assertEqual(suggestion['country_id']['display_name'], 'Sweden')
        self.assertIsInstance(suggestion['country_id']['id'], int)
        self.assertEqual(suggestion['vat'], 'SE556000123401')
        self.assertEqual(suggestion['company_registry'], '5560001234')
        # ``duns`` is our own handle, round-tripped by the widget.
        self.assertEqual(suggestion['duns'], 'foretagssok:abc123')

    def test_too_short_name_returns_empty(self):
        calls = []

        def handler(provider_key, ctx):
            calls.append(provider_key)
            return [{'name': 'X'}]

        self._install_provider(handler)
        self.assertEqual(self.partner_model.autocomplete_by_name('ab', False), [])
        self.assertEqual(calls, [])

    def test_deduplicates_on_organisation_number(self):
        """Two providers describing the same company must not give two rows."""
        def handler(provider_key, ctx):
            return [{
                'name': 'Testbolaget AB',
                'company_registry': '5560001234',
            }]

        self._install_provider(handler)
        result = self.partner_model.autocomplete_by_name('Testbolaget', False)
        self.assertEqual(len(result), 1)

    def test_reference_falls_back_to_organisation_number(self):
        """Without a provider id, the org number is the lookup key."""
        self._install_provider(lambda key, ctx: [{
            'name': 'Testbolaget AB',
            'company_registry': '5560001234',
        }])
        result = self.partner_model.autocomplete_by_name('Testbolaget', False)
        self.assertEqual(result[0]['duns'], 'foretagssok:5560001234')

    def test_rows_without_name_are_dropped(self):
        self._install_provider(lambda key, ctx: [
            {'city': 'Stockholm'},
            {'name': 'Namnlös AB'},
        ])
        result = self.partner_model.autocomplete_by_name('Test', False)
        self.assertEqual([r['name'] for r in result], ['Namnlös AB'])

    def test_country_zero_means_no_filter(self):
        seen = {}

        def handler(provider_key, ctx):
            seen[provider_key] = dict(ctx)
            return [{'name': 'Testbolaget AB'}]

        self._install_provider(handler)
        self.partner_model.autocomplete_by_name('Testbolaget', 0)
        self.assertFalse(seen['foretagssok']['country_code'])

    def test_provider_exception_yields_empty_list(self):
        def handler(provider_key, ctx):
            raise RuntimeError('down')

        self._install_provider(handler)
        self.assertEqual(self.partner_model.autocomplete_by_name('Test', False), [])


class TestEnrichByDuns(AutocompleteCase):

    def test_returns_data_wrapper(self):
        def handler(provider_key, ctx):
            if ctx.get('mode') != 'detail':
                return {}
            self.assertEqual(ctx['reference'], '5560001234')
            return {
                'name': 'Testbolaget AB',
                'city': 'Stockholm',
                'country_code': 'SE',
            }

        self._install_provider(handler)
        result = self.partner_model.enrich_by_duns('foretagssok:5560001234')
        self.assertNotIn('error', result)
        self.assertEqual(result['data']['name'], 'Testbolaget AB')
        self.assertEqual(result['data']['city'], 'Stockholm')
        # country_code is converted to the widget's many2one shape.
        self.assertEqual(result['data']['country_id']['display_name'], 'Sweden')
        self.assertNotIn('country_code', result['data'])

    def test_has_no_credit_error_key(self):
        """Nothing here is billed; an IAP top-up prompt would be a lie."""
        self._install_provider(lambda key, ctx: {'name': 'Testbolaget AB'})
        result = self.partner_model.enrich_by_duns('foretagssok:1')
        self.assertNotIn('credit_error', result)

    def test_unknown_provider_is_reported(self):
        self._install_provider(lambda key, ctx: {'name': 'X'})
        result = self.partner_model.enrich_by_duns('bolagsverket:5560001234')
        self.assertTrue(result['error'])
        self.assertIn('not enabled', result['error_message'])

    def test_bare_duns_number_is_reported(self):
        """An imported record's real DUNS has no provider we can use."""
        self._install_provider(lambda key, ctx: {'name': 'X'})
        result = self.partner_model.enrich_by_duns('123456789')
        self.assertTrue(result['error'])

    def test_provider_failure_is_reported_not_raised(self):
        def handler(provider_key, ctx):
            raise RuntimeError('down')

        self._install_provider(handler)
        result = self.partner_model.enrich_by_duns('foretagssok:1')
        self.assertTrue(result['error'])
        self.assertIn('could not be reached', result['error_message'])

    def test_empty_reference_is_reported(self):
        self._install_provider(lambda key, ctx: {})
        result = self.partner_model.enrich_by_duns(False)
        self.assertTrue(result['error'])


class TestWidgetIsMounted(TransactionCase):
    """The view inherit is the whole fix — assert it actually landed."""

    def test_company_registry_carries_the_widget(self):
        view = self.env['ir.ui.view'].search([
            ('model', '=', 'res.partner'),
            ('name', '=', 'res.partner.form.enrich.autocomplete'),
        ])
        self.assertTrue(view, 'The autocomplete view inherit is missing.')
        self.assertIn('field_partner_autocomplete', view.arch_db)

    def test_widget_reaches_the_rendered_form(self):
        """Compiled arch must contain the widget attribute on the field."""
        view = self.env['ir.ui.view'].search([
            ('model', '=', 'res.partner'),
            ('name', '=', 'res.partner.form.enrich.autocomplete'),
        ])
        self.assertTrue(view)
        combined = self.env['res.partner'].get_views(
            [(False, 'form')],
        )['views']['form']['arch']
        self.assertIn('field_partner_autocomplete', combined)
