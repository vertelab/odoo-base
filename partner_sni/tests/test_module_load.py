# -*- coding: utf-8 -*-
"""Load test for partner_sni.

Proves the module installs and that its models are in the registry.
It does not test behaviour: the port's acceptance criterion is that
the module loads on each edition, and this is what measures it.
"""
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPartnerSni(TransactionCase):

    def test_models_are_registered(self):
        """The models this module defines exist in the registry."""
        self.assertIn('res.sni', self.env)
        self.assertIn('res.partner', self.env)

    def test_module_is_installed(self):
        """The module loads and its data files were applied."""
        module = self.env['ir.module.module'].search(
            [('name', '=', 'partner_sni')])
        self.assertEqual(module.state, 'installed')
