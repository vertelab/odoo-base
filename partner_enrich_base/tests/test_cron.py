# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta
from unittest.mock import patch

from odoo import fields
from odoo.tests.common import TransactionCase


class CronCase(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_model = cls.env['res.partner']
        cls.params = cls.env['ir.config_parameter'].sudo()
        cls.params.set_param('partner_enrich.provider_order', 'foretagssok')

    def setUp(self):
        super().setUp()
        self.params.set_param('partner_enrich.refresh_days', '365')

    def _make(self, name, **vals):
        defaults = {'name': name, 'is_company': True}
        defaults.update(vals)
        return self.env['res.partner'].create(defaults)

    def _install_provider(self, handler):
        partner_model = type(self.partner_model)

        def _call(self, provider_key, ctx):
            return handler(provider_key, ctx)

        partner_model._enrich_from_provider = _call
        self.addCleanup(
            lambda: delattr(partner_model, '_enrich_from_provider'),
        )


class TestRefreshDays(CronCase):

    def test_default_is_365(self):
        self.params.set_param('partner_enrich.refresh_days', '')
        self.assertEqual(self.partner_model._enrich_refresh_days(), 365)

    def test_reads_the_parameter(self):
        self.params.set_param('partner_enrich.refresh_days', '30')
        self.assertEqual(self.partner_model._enrich_refresh_days(), 30)

    def test_garbage_falls_back_to_365(self):
        self.params.set_param('partner_enrich.refresh_days', 'aldrig')
        self.assertEqual(self.partner_model._enrich_refresh_days(), 365)

    def test_negative_is_clamped_to_zero(self):
        self.params.set_param('partner_enrich.refresh_days', '-5')
        self.assertEqual(self.partner_model._enrich_refresh_days(), 0)


class TestCronDomain(CronCase):

    def test_only_companies(self):
        """A private person has no organisation number to look up."""
        domain = self.partner_model._enrich_cron_domain(365)
        self.assertIn(('is_company', '=', True), domain)

    def test_only_active(self):
        domain = self.partner_model._enrich_cron_domain(365)
        self.assertIn(('active', '=', True), domain)

    def test_never_enriched_is_due(self):
        partner = self._make('Aldrig berikad AB')
        self.assertIn(partner, self.partner_model.search(
            self.partner_model._enrich_cron_domain(365),
        ))

    def test_recently_enriched_is_not_due(self):
        partner = self._make('Nyss berikad AB')
        partner.enrich_fetched_at = fields.Datetime.now()
        self.assertNotIn(partner, self.partner_model.search(
            self.partner_model._enrich_cron_domain(365),
        ))

    def test_stale_is_due(self):
        partner = self._make('Gammal AB')
        partner.enrich_fetched_at = fields.Datetime.now() - timedelta(days=400)
        self.assertIn(partner, self.partner_model.search(
            self.partner_model._enrich_cron_domain(365),
        ))

    def test_zero_days_means_everything(self):
        partner = self._make('Allt AB')
        partner.enrich_fetched_at = fields.Datetime.now()
        self.assertIn(partner, self.partner_model.search(
            self.partner_model._enrich_cron_domain(0),
        ))


class TestDryRun(CronCase):

    def test_dry_run_counts_without_writing(self):
        """The whole point: know what it would do before letting it do it."""
        self._make('Kandidat AB')
        with patch.object(
            type(self.partner_model), 'partner_enrich',
        ) as enrich:
            count = self.partner_model.with_context(
            enrich_commit_per_batch=False,
        )._enrich_cron(dry_run=True)
        self.assertGreaterEqual(count, 1)
        enrich.assert_not_called()

    def test_dry_run_leaves_fetched_at_untouched(self):
        partner = self._make('Orörd AB')
        self.partner_model.with_context(
            enrich_commit_per_batch=False,
        )._enrich_cron(dry_run=True)
        self.assertFalse(partner.enrich_fetched_at)

    def test_dry_run_with_nothing_due(self):
        self.env['res.partner'].search([]).write({
            'enrich_fetched_at': fields.Datetime.now(),
        })
        self.assertEqual(self.partner_model.with_context(
            enrich_commit_per_batch=False,
        )._enrich_cron(dry_run=True), 0)


class TestCronRun(CronCase):

    def test_runs_enrichment_on_due_records(self):
        partner = self._make('Berikas AB')
        self._install_provider(
            lambda key, ctx: {'city': 'Stockholm'},
        )
        self.partner_model.with_context(
            enrich_commit_per_batch=False,
        )._enrich_cron()
        self.assertEqual(partner.city, 'Stockholm')

    def test_skips_recently_enriched(self):
        partner = self._make('Hoppas över AB')
        partner.enrich_fetched_at = fields.Datetime.now()
        self._install_provider(lambda key, ctx: {'city': 'Stockholm'})
        self.partner_model.with_context(
            enrich_commit_per_batch=False,
        )._enrich_cron()
        self.assertFalse(partner.city)

    def test_batches_do_not_lose_records(self):
        """``split_every`` must cover every record, not just the first batch."""
        partners = self.env['res.partner']
        for index in range(5):
            partners |= self._make('Batch %s AB' % index)
        self.env['res.partner'].search([]).write({
            'enrich_fetched_at': fields.Datetime.now(),
        })
        partners.write({'enrich_fetched_at': False})
        self._install_provider(lambda key, ctx: {'city': 'Stockholm'})
        with patch.object(
            type(self.partner_model), 'ENRICH_CRON_BATCH', 2,
        ):
            # Assert the patch is live, or this test would pass trivially with
            # a batch size of 100 that fits all five in one go.
            self.assertEqual(self.partner_model.ENRICH_CRON_BATCH, 2)
            processed = self.partner_model.with_context(
                enrich_commit_per_batch=False,
            )._enrich_cron()
        self.assertGreaterEqual(processed, 5)
        for partner in partners:
            self.assertEqual(partner.city, 'Stockholm', partner.name)

    def test_returns_the_count(self):
        self._make('Räknas AB')
        self._install_provider(lambda key, ctx: {'city': 'Stockholm'})
        self.assertGreaterEqual(self.partner_model.with_context(
            enrich_commit_per_batch=False,
        )._enrich_cron(), 1)


class TestCronRecord(TransactionCase):

    def test_cron_exists_and_is_inactive(self):
        """A nightly job that switches itself on is a job nobody can trust."""
        cron = self.env.ref(
            'partner_enrich_base.ir_cron_enrich_refresh',
            raise_if_not_found=False,
        )
        self.assertTrue(cron, 'The refresh cron was not created.')
        self.assertFalse(
            cron.active,
            'The cron must ship inactive — enabling it is an operator decision.',
        )

    def test_cron_points_at_the_right_method(self):
        cron = self.env.ref('partner_enrich_base.ir_cron_enrich_refresh')
        self.assertIn('_enrich_cron', cron.code)
        self.assertEqual(cron.model_id.model, 'res.partner')
