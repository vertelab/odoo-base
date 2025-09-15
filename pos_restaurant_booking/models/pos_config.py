  # -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    booking_type_id = fields.Many2one('booking.type', string='Booking Type')
    module_pos_restaurant_booking = fields.Boolean("Table Booking")
