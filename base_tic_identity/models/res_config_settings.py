# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    tic_id = fields.Char(string='TIC ID', config_parameter='base_tic_identity.tic_id')
    tic_tenant = fields.Char(string='Tenant', config_parameter='base_tic_identity.tic_tenant')
    tic_api_key = fields.Char(string='API Key', config_parameter='base_tic_identity.tic_api_key')
