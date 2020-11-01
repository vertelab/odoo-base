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

class CalendarAppointment(models.Model):
    _inherit = 'calendar.appointment'

    def generate_cancel_daily_note(self, cancel_reason, appointment):
        super(CalendarAppointment, self).generate_cancel_daily_note(cancel_reason, appointment)
        #create daily note
        vals = {
            "name": _("Cancelled %s. Reason: %s" % (self.type_id.name, cancel_reason.name)),
            "partner_id": self.partner_id.id,
            "administrative_officer": self.user_id.id,
            "note": _("Cancelled %s: %s. Reason: %s" % (self.type_id.name, self.start, cancel_reason.name)) if self.channel_name == "PDM" else _("Cancelled %s: %s, %s %s. Reason: %s" % (self.type_id.name, self.start, self.office_id.office_code, self.user_id.login, cancel_reason.name)),
            "note_type": self.env.ref('partner_daily_notes.note_type_as_02').id,
            "office_id": self.partner_id.office_id.id,
            "note_date": self.start,
            "appointment_id": self.id,
        }
        appointment.partner_id.sudo().notes_ids = [(0, 0, vals)]
        # create edi message
        self.sudo().partner_id._create_next_last_msg()

    
    def generate_move_daily_note(self, occasions, reason):
        #create daily note
        vals = {
            "name": _("Meeting moved %s. Reason: %s" % (self.type_id.name, reason.name)),
            "partner_id": self.partner_id.id,
            "administrative_officer": self.user_id.id,
            "note": _("Meeting moved %s: %s. Reason: %s" % (self.type_id.name, self.start, reason.name)) if self.channel_name == "PDM" else _("Meeting moved %s: %s, %s %s. Reason: %s" % (self.type_id.name, self.start, self.office_id.office_code, self.user_id.login, reason.name)),
            "note_type": self.env.ref('partner_daily_notes.note_type_as_02').id,
            "office_id": self.partner_id.office_id.id,
            "appointment_id": self.id,
        }
        self.partner_id.sudo().notes_ids = [(0, 0, vals)]
        # create edi message
        self.sudo().partner_id._create_next_last_msg()



    @api.model
    def create(self, values):
        res = super(CalendarAppointment, self).create(values)

        if res.sudo().partner_id and res.state == 'confirmed':
            #create daily note
            vals = {
                    "name": _("Booked %s" % self.type_id.name),
                    "partner_id": self.partner_id.id,
                    "administrative_officer": self.user_id.id,
                    "note":_("Booked %s: %s." % (self.type_id.name, self.start)) if self.channel_name == "PDM" else _("Booked %s: %s, %s %s." % (self.type_id.name, self.start, self.office_id.office_code, self.user_id.login)),
                    "note_type": self.env.ref('partner_daily_notes.note_type_as_02').id,
                    "office_id": self.partner_id.office_id.id,
                    "note_date": self.start,
                    "appointment_id": self.id,
                }
            res.sudo().partner_id.notes_ids = [(0, 0, vals)]
            # create edi message
            self.appointment_id.sudo().partner_id._create_next_last_msg()

        return res

class CalendarAppointmentSuggestion(models.Model):
    _inherit = 'calendar.appointment.suggestion'

    @api.multi
    def _select_suggestion(self):
        super(CalendarAppointmentSuggestion, self)._select_suggestion()
        #create daily note
        vals = {
                "name": _("Booked %s" % self.appointment_id.type_id.name),
                "partner_id": self.appointment_id.partner_id.id,
                "administrative_officer": self.appointment_id.user_id.id,
                "note":_("Booked %s: %s." % (self.appointment_id.type_id.name, self.appointment_id.start)) if self.appointment_id.channel_name == "PDM" else _("Booked %s: %s, %s %s." % (self.appointment_id.type_id.name, self.appointment_id.start, self.appointment_id.office_id.office_code, self.appointment_id.user_id.login)),
                "note_type": self.env.ref('partner_daily_notes.note_type_as_02').id,
                "office_id": self.appointment_id.partner_id.office_id.id,
                "note_date": self.appointment_id.start,
                "appointment_id": self.appointment_id.id,
            }
        self.appointment_id.sudo().partner_id.notes_ids = [(0, 0, vals)]
        # create edi message
        self.appointment_id.sudo().partner_id._create_next_last_msg()