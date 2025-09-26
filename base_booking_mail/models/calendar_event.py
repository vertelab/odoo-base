from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class CalendarEvent(models.Model):
    _inherit = "calendar.event"

    booking_mail_calendar_ids = fields.One2many(comodel_name="booking.mail.calendar", inverse_name="calendar_event_id")

    @api.model_create_multi
    def create(self, vals_list):
        calendar_event_ids = super(CalendarEvent,self).create(vals_list)

        for calendar_event_id in calendar_event_ids:
            for booking_mail_id in calendar_event_id.booking_type_id.booking_mail_ids:
                self.env["booking.mail.calendar"].create({
                    "calendar_event_id": calendar_event_id.id,
                    "booking_mail_id": booking_mail_id.id,
                    "partner_ids": [(6, 0, calendar_event_id.partner_ids.ids)]
                })

        return calendar_event_ids


