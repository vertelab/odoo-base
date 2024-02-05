# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    portal_role_id = fields.Many2one(related="company_id.portal_role_id", string='Paper format', readonly=False,
                                     config_parameter='portal_role_id')
