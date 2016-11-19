# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution, third party addon
#    Copyright (C) 2004-2016 Vertel AB (<http://vertel.se>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class res_partner(models.Model):
    _inherit = 'res.partner'

    @api.one
    @api.depends('category_id', 'child_ids', 'child_ids.category_id')
    def _get_childs_categs(self):
        if self.is_company:
            categories = self.env['res.partner.category'].browse([])
            for c in self.child_ids:
                for categ in c.category_id:
                    categories |= categ
            self.child_category_ids = categories
    child_category_ids = fields.Many2many(comodel_name='res.partner.category', relation='res_partner_rel_res_partner_category_child', compute='_get_childs_categs', string='Child Tags', store=True)

    @api.one
    @api.depends('category_id', 'child_ids', 'child_ids.category_id', 'child_category_ids')
    def _get_missed_childs_categs(self):
        if self.is_company:
            categories = self.env['res.partner.category'].search([])
            self.missed_child_category_ids = categories - self.child_category_ids
    missed_child_category_ids = fields.Many2many(comodel_name='res.partner.category', relation='res_partner_rel_res_partner_all_category_child', compute='_get_missed_childs_categs', string='Missed Child Tags', store=True)
