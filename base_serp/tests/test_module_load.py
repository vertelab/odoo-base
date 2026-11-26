# -*- coding: utf-8 -*-
"""Load test for base_serp.

Proves the module installs and that its models are in the registry.
It does not test behaviour: the port's acceptance criterion is that
the module loads on each edition, and this is what measures it.
"""
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestBaseSerp(TransactionCase):

    def test_models_are_registered(self):
        """The models this module defines exist in the registry."""
        self.assertIn('res.partner', self.env)
        self.assertIn('serp.keyword', self.env)
        self.assertIn('serp.mixin', self.env)
        self.assertIn('serp.provider', self.env)
        self.assertIn('serp.result', self.env)
        self.assertIn('website.analytics.provider', self.env)

    def test_module_is_installed(self):
        """The module loads and its data files were applied."""
        module = self.env['ir.module.module'].search(
            [('name', '=', 'base_serp')])
        self.assertEqual(module.state, 'installed')
