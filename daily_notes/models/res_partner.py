# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution, third party addon
#    Copyright (C) 2004-2019 Vertel AB (<http://vertel.se>).
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

from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)

class ResPartnerNotes(models.Model):
    _description = 'Daily notes for a partner'
    _name = 'res.partner.notes'

    @api.multi
    def daily_notes_button(self, context=None):
#        dailynotes_id = self.env['res.partner'].search (
#            [('name', '=', "daily_notes.notes_tree_view")]).partner_id=self.partner.partner_id
#            )
        domain = []
#        domain = [('id','in',dailynotes_id)]
        view_id_tree = self.env['ir.ui.view'].search(
            [('name','=',"daily_notes.notes_tree_view")])partner_id=self.partner.partner_id
            )
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'daily.notes',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(view_id_tree[0].id, 'tree'),(False,'form')],
            'view_id ref="daily_notes.notes_tree_view"': '',
            'target': 'current',
            'domain': domain,
            }

class DailyNotes(models.Model):
    #_inherit = 'res.partner'
    _name = 'daily.notes'

    daily_notes = fields.One2many(comodel_name='daily.notes', 
                                 inverse_name='notes_id', 
                                 string='Daily notes id', 
                                 copy=False)
