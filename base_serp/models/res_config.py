# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    serp_max_position = fields.Integer(
        string='Maximum SERP Position',
        default=40,
        config_parameter='base_serp.max_position',
        help='Maximum position to track in search results. Results beyond this position will be ignored.'
    )