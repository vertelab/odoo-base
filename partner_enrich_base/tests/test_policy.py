# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class EnrichPolicyCase(TransactionCase):
    """Base for dispatcher tests: fake providers, no network, no IAP."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.policy = cls.env['res.partner.enrich.policy']
        cls.params = cls.env['ir.config_parameter'].sudo()
        cls.partner_model = cls.env['res.partner'].with_context(
            tracking_disable=True,
        )
        # Two fake providers, configured in this order. ``foretagssok`` comes
        # first, matching the shipped default.
        cls.params.set_str('partner_enrich.provider_order', 'foretagssok,allabolag')
        cls.partner = cls.partner_model.create({
            'name': '',
            'is_company': True,
            'country_id': cls.env.ref('base.se').id,
        })

    def _set_provider_data(self, data_by_provider):
        """Install a fake ``_enrich_from_provider`` on the partner model."""
        partner_model = type(self.partner)

        def _fake(self, provider_key, ctx):
            return data_by_provider.get(provider_key) or {}

        partner_model._enrich_from_provider = _fake
        self.addCleanup(lambda: delattr(partner_model, '_enrich_from_provider'))


class TestProviderKeys(EnrichPolicyCase):

    def test_default_order_when_unset(self):
        self.params.set_str('partner_enrich.provider_order', '')
        self.assertEqual(
            self.policy._enrich_provider_keys(), ['foretagssok', 'allabolag'],
        )

    def test_order_is_respected(self):
        self.params.set_str('partner_enrich.provider_order', 'allabolag, foretagssok')
        # Spaces around the comma must not become part of the key.
        self.assertEqual(
            self.policy._enrich_provider_keys(), ['allabolag', 'foretagssok'],
        )

    def test_empty_entries_are_dropped(self):
        self.params.set_str('partner_enrich.provider_order', 'a,,b,')
        self.assertEqual(self.policy._enrich_provider_keys(), ['a', 'b'])


class TestPolicy(EnrichPolicyCase):

    def test_default_is_fill_empty(self):
        self.params.set_str('partner_enrich.policy.identity', '')
        self.assertEqual(
            self.policy._enrich_policy('identity'), ('fill_empty', None),
        )

    def test_manual(self):
        self.params.set_str('partner_enrich.policy.identity', 'manual')
        self.assertEqual(self.policy._enrich_policy('identity'), ('manual', None))

    def test_prefer_known_provider(self):
        self.params.set_str('partner_enrich.policy.identity', 'prefer:allabolag')
        self.assertEqual(
            self.policy._enrich_policy('identity'), ('prefer', 'allabolag'),
        )

    def test_prefer_unknown_provider_falls_back(self):
        # A typo in the provider name must not stop enrichment; it falls back
        # to fill_empty rather than silently preferring nothing.
        self.params.set_str('partner_enrich.policy.identity', 'prefer:bolagsverket')
        self.assertEqual(
            self.policy._enrich_policy('identity'), ('fill_empty', None),
        )

    def test_prefer_without_name_falls_back(self):
        self.params.set_str('partner_enrich.policy.identity', 'prefer:')
        self.assertEqual(
            self.policy._enrich_policy('identity'), ('fill_empty', None),
        )

    def test_unknown_policy_falls_back(self):
        self.params.set_str('partner_enrich.policy.identity', 'yolo')
        self.assertEqual(
            self.policy._enrich_policy('identity'), ('fill_empty', None),
        )


class TestResolve(EnrichPolicyCase):

    def setUp(self):
        super().setUp()
        for group in ('identity', 'address', 'contact', 'classification'):
            self.params.set_str('partner_enrich.policy.%s' % group, '')

    def test_first_provider_wins_on_conflict(self):
        collected = [
            ('foretagssok', {'city': 'Stockholm'}),
            ('allabolag', {'city': 'Göteborg'}),
        ]
        self.assertEqual(
            self.policy._enrich_resolve(collected, {}), {'city': ('Stockholm', 'foretagssok')},
        )

    def test_second_provider_fills_what_first_lacks(self):
        collected = [
            ('foretagssok', {'city': 'Stockholm'}),
            ('allabolag', {'city': 'Göteborg', 'zip': '111 22'}),
        ]
        resolved = self.policy._enrich_resolve(collected, {})
        self.assertEqual(resolved['city'], ('Stockholm', 'foretagssok'))
        self.assertEqual(resolved['zip'], ('111 22', 'allabolag'))

    def test_fill_empty_keeps_existing_value(self):
        collected = [('foretagssok', {'city': 'Stockholm', 'zip': '111 22'})]
        resolved = self.policy._enrich_resolve(collected, {'city': 'Malmö'})
        self.assertEqual(resolved, {'zip': ('111 22', 'foretagssok')})

    def test_manual_writes_nothing(self):
        self.params.set_str('partner_enrich.policy.identity', 'manual')
        collected = [('foretagssok', {'name': 'Test AB', 'city': 'Stockholm'})]
        resolved = self.policy._enrich_resolve(collected, {})
        self.assertNotIn('name', resolved)
        # Other groups are untouched by the identity policy.
        self.assertEqual(resolved['city'], ('Stockholm', 'foretagssok'))

    def test_prefer_overrides_existing_value(self):
        self.params.set_str('partner_enrich.policy.identity', 'prefer:allabolag')
        collected = [
            ('foretagssok', {'name': 'Fel AB'}),
            ('allabolag', {'name': 'Rätt AB'}),
        ]
        resolved = self.policy._enrich_resolve(collected, {'name': 'Manuellt AB'})
        self.assertEqual(resolved['name'], ('Rätt AB', 'allabolag'))

    def test_prefer_without_data_falls_back_to_normal_precedence(self):
        # ``allabolag`` is preferred for identity but returned nothing for it;
        # the group must still be filled by whoever has data, not left empty.
        self.params.set_str('partner_enrich.policy.identity', 'prefer:allabolag')
        collected = [
            ('foretagssok', {'name': 'Test AB'}),
            ('allabolag', {'city': 'Stockholm'}),
        ]
        resolved = self.policy._enrich_resolve(collected, {})
        self.assertEqual(resolved['name'], ('Test AB', 'foretagssok'))

    def test_zero_is_not_empty(self):
        collected = [('foretagssok', {'financials': [{'fiscal_year': 2025, 'net_sales': 0}]})]
        resolved = self.policy._enrich_resolve(collected, {'financials': []})
        self.assertIn('financials', resolved)

    def test_unknown_key_is_ignored(self):
        collected = [('foretagssok', {'not_a_field': 'x', 'city': 'Stockholm'})]
        resolved = self.policy._enrich_resolve(collected, {})
        self.assertEqual(resolved, {'city': ('Stockholm', 'foretagssok')})


class TestPartnerEnrich(EnrichPolicyCase):
    """The orchestration itself, driven through ``partner_enrich()``."""

    def test_regression_first_provider_without_name_does_not_clear_it(self):
        """The ``crm_allabolag`` bug: a provider with no ``name`` wrote None.

        A provider that returns no data for a field must leave it exactly as it
        was — including when it is the *first* provider in the order.
        """
        self.partner.write({'name': 'Manuellt Namn AB'})
        self._set_provider_data({
            'foretagssok': {'city': 'Stockholm'},
            'allabolag': {'name': None, 'zip': '111 22'},
        })
        self.partner.partner_enrich()
        self.assertEqual(self.partner.name, 'Manuellt Namn AB')
        self.assertEqual(self.partner.city, 'Stockholm')
        self.assertEqual(self.partner.zip, '111 22')

    def test_writes_fields_and_bookkeeping(self):
        self._set_provider_data({
            'foretagssok': {
                'name': 'Testbolaget AB',
                'company_registry': '5560001234',
                'city': 'Stockholm',
                'website': 'https://example.se',
            },
        })
        self.partner.partner_enrich()
        self.assertEqual(self.partner.name, 'Testbolaget AB')
        self.assertEqual(self.partner.company_registry, '5560001234')
        self.assertEqual(self.partner.city, 'Stockholm')
        self.assertEqual(self.partner.website, 'https://example.se')
        self.assertEqual(self.partner.enrich_provider, 'foretagssok')
        self.assertTrue(self.partner.enrich_fetched_at)
        self.assertIn('Testbolaget AB', self.partner.enrich_raw)

    def test_country_code_becomes_country_id(self):
        self.partner.write({'country_id': False})
        self._set_provider_data({'foretagssok': {'country_code': 'NO'}})
        self.partner.partner_enrich()
        self.assertEqual(self.partner.country_id.code, 'NO')

    def test_unknown_country_code_is_skipped(self):
        self.partner.write({'country_id': False})
        self._set_provider_data({'foretagssok': {'country_code': 'XX'}})
        self.partner.partner_enrich()
        self.assertFalse(self.partner.country_id)

    def test_provider_exception_does_not_stop_the_run(self):
        partner_model = type(self.partner)

        def _boom(self, provider_key, ctx):
            if provider_key == 'foretagssok':
                raise RuntimeError('API is down')
            return {'city': 'Stockholm'}

        partner_model._enrich_from_provider = _boom
        self.addCleanup(lambda: delattr(partner_model, '_enrich_from_provider'))

        self.partner.partner_enrich()
        self.assertEqual(self.partner.city, 'Stockholm')
        self.assertEqual(self.partner.enrich_provider, 'allabolag')

    def test_nothing_returned_writes_nothing(self):
        self._set_provider_data({})
        self.partner.partner_enrich()
        self.assertFalse(self.partner.enrich_fetched_at)

    def test_policy_manual_blocks_write_but_keeps_bookkeeping(self):
        self.params.set_str('partner_enrich.policy.identity', 'manual')
        self._set_provider_data({'foretagssok': {'name': 'Ny AB', 'city': 'Stockholm'}})
        self.partner.partner_enrich()
        self.assertNotEqual(self.partner.name, 'Ny AB')
        self.assertEqual(self.partner.city, 'Stockholm')

    def test_second_run_is_idempotent(self):
        """Re-running must not change what the first run produced.

        This is the whole point of ``fill_empty``: the first run writes, the
        second sees the values already there and leaves them alone.
        """
        self._set_provider_data({
            'foretagssok': {'name': 'Testbolaget AB', 'city': 'Stockholm'},
            'allabolag': {'zip': '111 22'},
        })
        self.partner.partner_enrich()
        first = {
            'name': self.partner.name,
            'city': self.partner.city,
            'zip': self.partner.zip,
            'provider': self.partner.enrich_provider,
        }
        self.partner.partner_enrich()
        self.assertEqual(self.partner.name, first['name'])
        self.assertEqual(self.partner.city, first['city'])
        self.assertEqual(self.partner.zip, first['zip'])
        self.assertEqual(self.partner.enrich_provider, first['provider'])
