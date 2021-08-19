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

from odoo import models, fields, api, _
from datetime import datetime, timedelta
import logging
import pytz

_logger = logging.getLogger(__name__)


def datetime_se2utc(dt):
    tz_se = pytz.timezone('Europe/Stockholm')
    tz_utc = pytz.timezone('UTC')
    dt = tz_se.localize(dt)
    return tz_utc.normalize(dt).replace(tzinfo=None)


def datetime_utc2se(dt):
    tz_se = pytz.timezone('Europe/Stockholm')
    tz_utc = pytz.timezone('UTC')
    dt = tz_utc.localize(dt)
    return tz_se.normalize(dt).replace(tzinfo=None)


class ResPartnerNotes(models.Model):
    _description = "Daily notes for a partner"
    _name = "res.partner.notes"

    name = fields.Char(string="Title")
    partner_id = fields.Many2one(comodel_name="res.partner", string="Job seeker")

    administrative_officer = fields.Many2one(
        "res.users", string="Administrative officer", default=lambda self: self.env.user
    )
    note = fields.Text(string="Notes")
    note_date = fields.Datetime(string="Refers to date", default=fields.Datetime.now)
    is_confidential = fields.Boolean(string="Secret", help="Apply/Remove Secret")
    note_type = fields.Many2one(comodel_name="res.partner.note.type")
    note_number = fields.Char(string="AIS number")
    appointment_id = fields.Many2one(
        comodel_name="calendar.appointment", string="Linked meeting"
    )
    office_id = fields.Many2one("hr.department", string="Office")
    customer_id = fields.Char(
        string="Customer number", related="partner_id.customer_id"
    )


class ResPartner(models.Model):
    _inherit = "res.partner"

    notes_ids = fields.One2many(
        comodel_name="res.partner.notes",
        string="Daily notes",
        inverse_name="partner_id",
    )
    next_contact_date = fields.Date(
        string="Next contact",
        help="Fields used by AIS-F data. Do not overwrite with other data.",
    )
    next_contact_time = fields.Char(
        string="Next contact time",
        help="Fields used by AIS-F data. Do not overwrite with other data.",
    )
    next_contact_type = fields.Selection(
        string="Next contact type",
        selection=[
            ("T", "Phone"),
            ("B", "Visit"),
            ("E", "E-mail"),
            ("P", "Mail"),
            ("I", "Internet"),
        ],
        help="Fields used by AIS-F data. Do not overwrite with other data.",
    )
    last_contact_date = fields.Date(
        string="Latest contact",
        help="Fields used by AIS-F data. Do not overwrite with other data.",
    )
    last_contact_type = fields.Selection(
        string="Latest contact type",
        selection=[
            ("T", "Phone"),
            ("B", "Visit"),
            ("E", "E-mail"),
            ("P", "Mail"),
            ("I", "Internet"),
        ],
        help="Fields used by AIS-F data. Do not overwrite with other data.",
    )

    # these fields are used to present the information in views.
    next_contact = fields.Char(string="Next contact", compute="_compute_next_contact")
    last_contact = fields.Char(string="Latest contact", compute="_compute_last_contact")
    # these fields are used to keep track of our internal next / last contact dates
    # and decide weather we need to sync our data to AIS-F or not.
    next_contact_app = fields.Datetime(
        string="Next contact (appointment)", compute="_compute_next_contact"
    )
    last_contact_app = fields.Datetime(
        string="Latest contact (appointment)", compute="_compute_last_contact"
    )
    last_contact_type_app = fields.Selection(
        string="Latest contact type",
        selection=[
            ("T", "Phone"),
            ("B", "Visit"),
            ("E", "E-mail"),
            ("P", "Mail"),
            ("I", "Internet"),
        ],
    )
    next_contact_type_app = fields.Selection(
        string="Next contact type",
        selection=[
            ("T", "Phone"),
            ("B", "Visit"),
            ("E", "E-mail"),
            ("P", "Mail"),
            ("I", "Internet"),
        ],
    )

    @api.one
    def _compute_next_contact(self):
        # get the first planned meeting for the jobseeker
        appointment = self.env["calendar.appointment"].search(
            [
                ("partner_id", "=", self.id),
                ("state", "=", "confirmed"),
                ("start", ">=", datetime.now()),
            ],
            order="start",
            limit=1,
        )
        next_contact_date = None
        next_contact_time = None
        next_contact_type = None
        res = _("No next contact")
        res_datetime = False
        if appointment and (
                not self.next_contact_date
                or (
                        self.next_contact_date
                        and appointment.start.date() < self.next_contact_date
                )
        ):
            # use appointment date instead of AIS-F data.

            next_contact_time = \
                datetime_utc2se(appointment.start).strftime("%H:%M")
            next_contact_date = appointment.start.date()
            next_contact_type = (
                "T"
                if appointment.channel == self.env.ref("calendar_channel.channel_pdm")
                else "B"
            )
            res_datetime = appointment.start
        elif self.next_contact_date and self.next_contact_time:
            # use AIS-F data
            next_contact_time = self.next_contact_time
            next_contact_date = self.next_contact_date
            next_contact_type = self.next_contact_type
            res_datetime = datetime_se2utc(datetime.combine(
                next_contact_date,
                datetime.strptime(next_contact_time, "%H:%M").time()
            ))
        if next_contact_date:
            res = f"{next_contact_date} {next_contact_time if next_contact_time else ''} {next_contact_type}"
        self.next_contact = res
        self.next_contact_app = res_datetime
        self.next_contact_type_app = next_contact_type

    @api.one
    def _compute_last_contact(self):
        # get the last historic meeting for the jobseeker
        appointment = self.env["calendar.appointment"].search(
            [
                ("partner_id", "=", self.id),
                ("state", "=", "done"),
                ("start", "<", datetime.now()),
            ],
            order="start",
            limit=1,
        )
        res_datetime = False
        if appointment and (
                not self.next_contact_date
                or (
                        self.last_contact_date
                        and appointment.start.date() > self.last_contact_date
                )
        ):
            # use appointment date instead of AIS-F data.
            last_contact_date = appointment.start.date()
            last_contact_type = (
                "T"
                if appointment.channel == self.env.ref("calendar_channel.channel_pdm")
                else "B"
            )
            res_datetime = appointment.start
        else:
            # use AIS-F data
            last_contact_date = (
                self.last_contact_date if self.last_contact_date else False
            )
            last_contact_type = self.last_contact_type
            res_datetime = datetime.combine(last_contact_date, datetime.min.time())
        if last_contact_date:
            res = f"{last_contact_date} {last_contact_type}"
        else:
            res = _("No last contact")
        self.last_contact = res
        self.last_contact_app = res_datetime
        self.last_contact_type_app = last_contact_type

    @api.multi
    def _create_next_last_msg(self):
        try:
            if self.is_jobseeker:
                route = self.env.ref(
                    "edi_af_aisf_trask.asok_contact_route", raise_if_not_found=False
                )
                if route:
                    vals = {
                        "name": "set contact msg",
                        "edi_type": self.env.ref("edi_af_aisf_trask.asok_contact").id,
                        "model": self._name,
                        "res_id": self.id,
                        "route_id": route.id,
                        "route_type": "edi_af_aisf_trask_contact",
                    }
                    message = self.env["edi.message"].create(vals)
                    message.pack()
                    route.run()
        except:
            _logger.exception("Something went wrong in IPF meeting sync.")

    def action_view_next_event(self):
        action = {
            "name": _(self.name + " - notes"),
            "domain": [("partner_id", "=", self.ids)],
            "view_type": "form",
            "res_model": "res.partner.notes",
            "view_id": self.env.ref("partner_daily_notes.partner_notes_view_tree").id,
            "view_mode": "tree",
            "type": "ir.actions.act_window",
        }
        if len(self) == 1:
            action["context"] = {"default_partner_id": self.id}
        return action


class ResPartnerNoteType(models.Model):
    _name = "res.partner.note.type"
    _rec_name = "description"

    note_id = fields.One2many(
        comodel_name="res.partner.notes", inverse_name="note_type"
    )
    name = fields.Char(string="Name")
    description = fields.Char(string="Description")
