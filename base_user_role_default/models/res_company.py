# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class Company(models.Model):
    _inherit = 'res.company'

    portal_role_id = fields.Many2one('res.users.role', 'User Role')
