import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError

_logger = logging.getLogger(__name__)

class BookingMail(models.Model):
    _name = 'booking.mail'
    _rec_name = "booking_type_id"
    _description = 'Booking Automated Mailing'

    booking_type_id = fields.Many2one(comodel_name="booking.type", required=True, ondelete='cascade')
    sequence = fields.Integer('Display order')
    interval_nbr = fields.Integer('Interval', default=1)
    interval_unit = fields.Selection([
        ('now', 'Immediately'),
        ('hours', 'Hours'), ('days', 'Days'),
        ('weeks', 'Weeks'), ('months', 'Months')],
        string='Unit', default='hours', required=True)
    interval_type = fields.Selection([
        ('after_sub', 'After each registration'),
        ('before_event', 'Before the event'),
        ('after_event', 'After the event')],
        string='Trigger ', default="before_event", required=True)
    mail_count_done = fields.Integer('# Sent', copy=False, compute="_compute_mail_count_done")
    template_ref = fields.Reference(string='Template', ondelete={'mail.template': 'cascade'}, required=True, selection=[('mail.template', 'Mail')])
    mail_state = fields.Selection(
        [('running', 'Running'), ('scheduled', 'Scheduled'), ('sent', 'Sent')],
        string='Global communication Status', compute='_compute_mail_state')
    booking_mail_calendar_ids = fields.One2many(comodel_name="booking.mail.calendar", inverse_name="booking_mail_id")
    mail_done = fields.Boolean("Sent", copy=False, compute="_compute_mail_done")
    scheduled_date = fields.Datetime('Schedule Date', compute='_compute_scheduled_date')

    def _compute_scheduled_date(self):
        for scheduler in self:
            if scheduler.booking_mail_calendar_ids and scheduler.booking_mail_calendar_ids[0].scheduled_date:
                scheduler.scheduled_date = scheduler.booking_mail_calendar_ids[0].scheduled_date
            else:
                scheduler.scheduled_date = False

    def _compute_mail_done(self):
        for scheduler in self:
            if scheduler.booking_mail_calendar_ids:
                scheduler.mail_done = all(scheduler.booking_mail_calendar_ids.mapped("mail_done"))
            else:
                scheduler.mail_done = False

    def _compute_mail_count_done(self):
        for scheduler in self:
            if scheduler.booking_mail_calendar_ids:
                mail_count_done = scheduler.booking_mail_calendar_ids.mapped("mail_count_done")
                if mail_count_done:
                    scheduler.mail_count_done = sum(mail_count_done)/len(mail_count_done)
                else:
                    scheduler.mail_count_done = 0
            else:
                scheduler.mail_count_done = False

    @api.depends('interval_type', 'mail_done')
    def _compute_mail_state(self):
        for scheduler in self:
            # registrations based
            if scheduler.interval_type == 'after_sub':
                scheduler.mail_state = 'running'
            # global event based
            elif scheduler.mail_done:
                scheduler.mail_state = 'sent'
            else:
                scheduler.mail_state = 'scheduled'