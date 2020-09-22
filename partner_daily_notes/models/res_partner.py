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

    name = fields.Char(string="Title") 
    partner_id = fields.Many2one(comodel_name="res.partner", string="Job seeker")

    administrative_officer = fields.Many2one('res.users', string='Administrative officer', default=lambda self: self.env.user)
    note = fields.Text(string="Notes")
    note_date = fields.Datetime(string="Refers to date", default=fields.Datetime.now)
    is_confidential = fields.Boolean(string="Secret", help="Apply/Remove Secret")
    note_type = fields.Many2one(comodel_name="res.partner.note.type")
    note_number = fields.Char(string="AIS number")

    office_id = fields.Many2one('hr.department', string="Office")
    customer_id = fields.Char(string="Customer number", related="partner_id.customer_id")

class ResPartner(models.Model):
    _inherit = 'res.partner'

    notes_ids = fields.One2many(comodel_name='res.partner.notes', 
                                 string='Daily notes', inverse_name="partner_id")

    @api.one
    def compute_notes_count(self):
        for partner in self:
            partner.notes_count = len(partner.notes_ids)

    notes_count = fields.Integer(compute='compute_notes_count')

    @api.multi
    def view_notes(self):
        action = {
            'name': _('Daily notes'),
            'domain': [('partner_id', '=', self.ids)],
            'view_type': 'form',
            'res_model': 'res.partner.notes',
            'view_id': self.env.ref('partner_daily_notes.partner_notes_view_tree_button').id, #self.env['ir.model.data'].get_object_reference('partner_daily_notes','view_partner_notes_tree_button'),
            'view_mode': 'tree', 
            'type': 'ir.actions.act_window',
        }
        if len(self) == 1:
            action['context'] = {'default_partner_id': self.id}
        return action


class ResPartnerNoteType(models.Model):
    _name = "res.partner.note.type"
    _rec_name = 'description'

    note_id = fields.One2many(comodel_name="res.partner.notes", inverse_name="note_type")
    name = fields.Char(string="Name")
    description = fields.Char(string="Description")
