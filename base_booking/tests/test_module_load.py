# -*- coding: utf-8 -*-
"""Load test for base_booking.

Proves the module installs and that its models are in the registry.
It does not test behaviour: the port's acceptance criterion is that
the module loads on each edition, and this is what measures it.
"""
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestBaseBooking(TransactionCase):

    def test_models_are_registered(self):
        """The models this module defines exist in the registry."""
        self.assertIn('booking.answer', self.env)
        self.assertIn('booking.answer.input', self.env)
        self.assertIn('booking.invite', self.env)
        self.assertIn('booking.line', self.env)

    def test_module_is_installed(self):
        """The module loads and its data files were applied."""
        module = self.env['ir.module.module'].search(
            [('name', '=', 'base_booking')])
        self.assertEqual(module.state, 'installed')
