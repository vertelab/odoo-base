  # -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_booking_type_id = fields.Many2one(related="pos_config_id.booking_type_id", readonly=False)
    pos_module_pos_restaurant_booking = fields.Boolean(related="pos_config_id.module_pos_restaurant_booking", readonly=False)
