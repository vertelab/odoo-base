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

    administrative_officer = fields.Many2one('res.users',
                                 string='Administrative officer',
                                 default=lambda self: self.env.user)
    note = fields.Text(string="Notes")
    note_date = fields.Datetime(string="Refers to date", default=fields.Datetime.now)
    is_confidential = fields.Boolean(string="Secret", help="Apply/Remove Secret")
    note_type = fields.Many2one(comodel_name="res.partner.note.type")
    note_number = fields.Char(string="AIS number")
    
    appointment_id = fields.Many2one(comodel_name='calendar.appointment',
                                 string='Linked meeting')
    office_id = fields.Many2one('hr.department', string="Office")
    customer_id = fields.Char(string="Customer number", related="partner_id.customer_id")

class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.depends('notes_ids')
    def _compute_note_fields(self):
        for partner in self:
            daily_note_last_contact = self.env['res.partner.notes'].search([
                ('partner_id', '=', partner.id), ('note_date', '<=', fields.Date.today())],
                limit=1, order='note_date desc')
            if daily_note_last_contact:
                partner.last_contact = daily_note_last_contact.note_date.date()
                # check that we have a linked appointment
                if daily_note_last_contact.appointment_id:
                    partner.last_contact_type = 'T' if daily_note_last_contact.appointment_id.channel == self.env.ref('calendar_channel.channel_pdm') else 'B'

            daily_note_next_contact = self.env['res.partner.notes'].search([
                ('partner_id', '=', partner.id), ('note_date', '>', fields.Date.today())],
                limit=1, order='note_date desc')
            if daily_note_next_contact:
                partner.next_contact = daily_note_next_contact.note_date.date()
                partner.next_contact_time = daily_note_next_contact.note_date.strftime("%H:%M")
                # check that we have a linked appointment
                if daily_note_next_contact.appointment_id:
                    partner.next_contact_type = 'T' if daily_note_next_contact.appointment_id.channel == self.env.ref('calendar_channel.channel_pdm') else 'B'

    @api.multi
    def _create_next_last_msg(self):
        if self.is_jobseeker:
            route = self.env.ref('edi_af_aisf_trask.asok_contact_route', raise_if_not_found=False)
            if route:
                vals = {
                    'name': 'set contact msg',
                    'edi_type': self.env.ref('edi_af_aisf_trask.asok_contact').id,
                    'model': self._name,
                    'res_id': self.id,
                    'route_id': route.id,
                    'route_type': 'edi_af_aisf_trask_contact',
                }
                message = self.env['edi.message'].create(vals)
                message.pack()

    notes_ids = fields.One2many(comodel_name='res.partner.notes', 
                                 string='Daily notes', inverse_name="partner_id")
    next_contact = fields.Date(string="Next contact", compute='_compute_note_fields',
                                 store=True)
    next_contact_time = fields.Char(string='Next contact time', 
                                 compute='_compute_note_fields', store=True)
    next_contact_type = fields.Selection(string='Next contact type', 
                                selection=[('T', 'Phone'), ('B', 'Visit'),
                                 ('E', 'E-mail'), ('P', 'Mail'), ('I', 'Internet')],
                                  compute='_compute_note_fields', store=True)
    last_contact = fields.Date(string="Last contact", compute='_compute_note_fields',
                                 store=True)
    last_contact_type = fields.Selection(string='Last contact type',
                                 selection=[('T', 'Phone'), ('B', 'Visit'),
                                  ('E', 'E-mail'), ('P', 'Mail'), ('I', 'Internet')],
                                   compute='_compute_note_fields', store=True)

    def action_view_next_event(self):
        action = {
            'name': _(self.name + ' - notes'),
            'domain': [('partner_id', '=', self.ids)],
            'view_type': 'form',
            'res_model': 'res.partner.notes',
            'view_id': self.env.ref('partner_daily_notes.partner_notes_view_tree').id,
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
