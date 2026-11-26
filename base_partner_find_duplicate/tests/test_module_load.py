# -*- coding: utf-8 -*-
"""Load test for base_partner_find_duplicate.

Proves the module installs and that its models are in the registry.
It does not test behaviour: the port's acceptance criterion is that
the module loads on each edition, and this is what measures it.
"""
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestBasePartnerFindDuplicate(TransactionCase):

    def test_module_is_installed(self):
        """The module loads and its data files were applied."""
        module = self.env['ir.module.module'].search(
            [('name', '=', 'base_partner_find_duplicate')])
        self.assertEqual(module.state, 'installed')
