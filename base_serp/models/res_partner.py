# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = ['res.partner', 'serp.mixin']

    # Markera kontakter som SERP-övervakade. Utan flaggan visas inga
    # SERP-fält och inga requirement-fält tvingas (samma mönster som
    # is_keykeep_partner / is_bifrost_provider).
    is_serp = fields.Boolean(string='SERP', default=False)

    serp_keyword_ids = fields.One2many('serp.keyword', 'partner_id', string='Keywords')
