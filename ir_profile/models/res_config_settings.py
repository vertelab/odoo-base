# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'

    profiling_enabled_until = fields.Datetime("Profiling enabled until",
                                              config_parameter='base.profiling_enabled_until')
