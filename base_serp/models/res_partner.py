# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = ['res.partner', 'serp.mixin']

    serp_keyword_ids = fields.One2many('serp.keyword', 'partner_id', string='Keywords')
