import logging
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError

_logger = logging.getLogger(__name__)

_INTERVALS = {
    'hours': lambda interval: relativedelta(hours=interval),
    'days': lambda interval: relativedelta(days=interval),
    'weeks': lambda interval: relativedelta(days=7*interval),
    'months': lambda interval: relativedelta(months=interval),
    'now': lambda interval: relativedelta(hours=0),
}

class BookingMailCalendar(models.Model):
    _name = 'booking.mail.calendar'
    _description = 'Glue model between booking.mail and calendar.event'

    booking_mail_id = fields.Many2one(comodel_name="booking.mail")
    calendar_event_id = fields.Many2one(comodel_name="calendar.event")
    scheduled_date = fields.Datetime('Schedule Date', compute='_compute_scheduled_date', store=True)
    interval_nbr = fields.Integer('Interval', related="booking_mail_id.interval_nbr")
    interval_unit = fields.Selection([
        ('now', 'Immediately'),
        ('hours', 'Hours'), ('days', 'Days'),
        ('weeks', 'Weeks'), ('months', 'Months')],
        string='Unit', default='hours', required=True, related="booking_mail_id.interval_unit")
    interval_type = fields.Selection([
        ('after_sub', 'After each registration'),
        ('before_event', 'Before the event'),
        ('after_event', 'After the event')],
        string='Trigger ', default="before_event", required=True, related="booking_mail_id.interval_type")
    mail_done = fields.Boolean("Sent", copy=False, readonly=True)
    partner_ids = fields.Many2many(comodel_name="res.partner")
    mail_count_done = fields.Integer('# Sent', copy=False, readonly=True)

    @api.depends('calendar_event_id.start_date', 'calendar_event_id.stop_date', 'interval_type', 'interval_unit', 'interval_nbr')
    def _compute_scheduled_date(self):
        for scheduler in self:
            if scheduler.interval_type == 'after_sub':
                date, sign = scheduler.calendar_event_id.create_date, 1
            elif scheduler.interval_type == 'before_event':
                date, sign = scheduler.calendar_event_id.start_date, -1
            else:
                date, sign = scheduler.calendar_event_id.stop_date, 1

            scheduler.scheduled_date = date + _INTERVALS[scheduler.interval_unit](sign * scheduler.interval_nbr) if date else False