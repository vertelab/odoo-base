# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution, third party addon
#    Copyright (C) 2004-2021 Vertel AB (<http://vertel.se>).
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

from datetime import datetime
import pytz
from odoo import models, fields, api, _
import logging
from odoo import SUPERUSER_ID

_logger = logging.getLogger(__name__)


class CalendarAppointment(models.Model):
    _inherit = "calendar.appointment"

    def generate_cancel_daily_note(self, cancel_reason, appointment):
        super(CalendarAppointment, self).generate_cancel_daily_note(
            cancel_reason, appointment
        )
        tz = pytz.timezone("Europe/Stockholm")
        current_time = datetime.now(tz=tz)
        # create daily note
        user = self.env.context.get("uid")
        user = user and self.env["res.users"].browse(user) or self.env.user
        vals = {
            "name": _(
                "Cancelled %s. Reason: %s" % (self.type_id.name, cancel_reason.name)
            ),
            "partner_id": self.partner_id.id,
            "administrative_officer": user if user.id != SUPERUSER_ID else False,
            "note": _(
                "Cancelled %s: %s. Reason: %s"
                % (self.type_id.name, self.start, cancel_reason.name)
            ),
            "note_type": self.env.ref("partner_daily_notes.note_type_as_02").id,
            "office_id": user.office_ids._ids[0] if user.office_ids else False,
            "note_date": current_time,
            "appointment_id": self.id,
        }
        if self.channel_name != "PDM":
            vals["note"] = _(
                "Cancelled %s: %s, %s %s. Reason: %s"
                % (
                    self.type_id.name,
                    current_time,
                    self.office_id.office_code,
                    self.user_id.login,
                    cancel_reason.name,
                )
            )
        appointment.partner_id.sudo().notes_ids = [(0, 0, vals)]
        # create edi message
        self.sudo().partner_id._create_next_last_msg()

    def generate_move_daily_note(self, occasions, reason):
        # create daily note
        tz = pytz.timezone("Europe/Stockholm")
        current_time = datetime.now(tz=tz)
        user = self.env.context.get("uid")
        user = user and self.env["res.users"].browse(user) or self.env.user
        vals = {
            "name": _(
                "Meeting moved %s. Reason: %s" % (self.type_id.name, reason.name)
            ),
            "note":  _(
                "Meeting moved %s: %s. Reason: %s"
                % (self.type_id.name, self.start, reason.name)
            ),
            "partner_id": self.partner_id.id,
            "administrative_officer": user if user.id != SUPERUSER_ID else False,
            "note_type": self.env.ref("partner_daily_notes.note_type_as_02").id,
            "office_id": user.office_ids._ids[0] if user.office_ids else False,
            "appointment_id": self.id,
        }
        if self.channel_name != "PDM":
            vals["note"] = _(
                "Meeting moved %s: %s, %s %s. Reason: %s"
                % (
                    self.type_id.name,
                    current_time,
                    self.office_id.office_code,
                    self.user_id.login,
                    reason.name,
                )
            )
        self.partner_id.sudo().notes_ids = [(0, 0, vals)]
        # create edi message
        self.sudo().partner_id._create_next_last_msg()

    @api.model
    def create(self, values):
        res = super(CalendarAppointment, self).create(values)
        tz = pytz.timezone("Europe/Stockholm")
        current_time = datetime.now(tz=tz)
        user = self.env.context.get("uid")
        user = user and self.env["res.users"].browse(user) or self.env.user
        if res.sudo().partner_id and res.state == "confirmed":
            # create daily note
            vals = {
                "name": _("Booked %s" % self.type_id.name),
                "partner_id": self.partner_id.id,
                "administrative_officer": user if user.id != SUPERUSER_ID else False,
                "note": _("Booked %s: %s." % (self.type_id.name, self.start)),
                "note_type": self.env.ref("partner_daily_notes.note_type_as_02").id,
                "office_id": user.office_ids._ids[0] if user.office_ids else False,
                "note_date": current_time,
                "appointment_id": self.id,
            }
            if self.channel_name != "PDM":
                vals["note"] = _(
                    "Booked %s: %s, %s %s."
                    % (
                        self.type_id.name,
                        current_time,
                        self.office_id.office_code,
                        self.user_id.login,
                    )
                )
            res.sudo().partner_id.notes_ids = [(0, 0, vals)]
            # create edi message
            res.sudo().partner_id._create_next_last_msg()

        return res


class CalendarAppointmentSuggestion(models.Model):
    _inherit = "calendar.appointment.suggestion"

    @api.multi
    def _select_suggestion(self):
        super(CalendarAppointmentSuggestion, self)._select_suggestion()
        user = self.env.context.get("uid")
        user = user and self.env["res.users"].browse(user) or self.env.user
        # create daily note
        vals = {
            "name": _("Booked %s" % self.appointment_id.type_id.name),
            "partner_id": self.appointment_id.partner_id.id,
            "administrative_officer": user if user.id != SUPERUSER_ID else False,
            "note": _(
                "Booked %s: %s."
                % (self.appointment_id.type_id.name, self.appointment_id.start)
            ),
            "note_type": self.env.ref("partner_daily_notes.note_type_as_02").id,
            "office_id": user.office_ids._ids[0] if user.office_ids else False,
            "note_date": self.appointment_id.start,
            "appointment_id": self.appointment_id.id,
        }
        if self.appointment_id.channel_name != "PDM":
            vals["note"] = _(
                "Booked %s: %s, %s %s."
                % (
                    self.appointment_id.type_id.name,
                    self.appointment_id.start,
                    self.appointment_id.office_id.office_code,
                    self.appointment_id.user_id.login,
                )
            )
        partner = self.appointment_id.sudo().partner_id
        partner.notes_ids = [(0, 0, vals)]

        # create edi message
        partner._create_next_last_msg()
