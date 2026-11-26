# -*- coding: utf-8 -*-
"""Load test for ir_module_xl2install.

Proves the module installs and that its models are in the registry.
It does not test behaviour: the port's acceptance criterion is that
the module loads on each edition, and this is what measures it.
"""
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestIrModuleXl2install(TransactionCase):

    def test_models_are_registered(self):
        """The models this module defines exist in the registry."""
        self.assertIn('ir.module.install_wizard.missing_module', self.env)
        self.assertIn('ir.module.install_wizard.to_be_installed', self.env)
        self.assertIn('ir.module.install_wizard.enterprise', self.env)
        self.assertIn('ir.module.install_wizard', self.env)

    def test_module_is_installed(self):
        """The module loads and its data files were applied."""
        module = self.env['ir.module.module'].search(
            [('name', '=', 'ir_module_xl2install')])
        self.assertEqual(module.state, 'installed')
