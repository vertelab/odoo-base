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
    template_ref = fields.Reference(string='Template', required=True, related="booking_mail_id.template_ref")

    @api.model_create_multi
    def create(self, vals_list):
        booking_mail_calendar_ids = super(BookingMailCalendar,self).create(vals_list)

        for booking_mail_calendar_id in booking_mail_calendar_ids:
            if booking_mail_calendar_id.interval_type == "after_sub" and booking_mail_calendar_id.interval_unit == "now":
                for partner_id in booking_mail_calendar_id.partner_ids:
                    _logger.error(f"{partner_id.name=}")
                    booking_mail_calendar_id._send_mail(partner_id)
                    booking_mail_calendar_id.mail_count_done += 1 
                booking_mail_calendar_id.mail_done = True

        return booking_mail_calendar_ids

    @api.depends('calendar_event_id.start', 'calendar_event_id.stop', 'interval_type', 'interval_unit', 'interval_nbr')
    def _compute_scheduled_date(self):
        for scheduler in self:
            if scheduler.interval_type == 'after_sub':
                date, sign = scheduler.calendar_event_id.create_date, 1
            elif scheduler.interval_type == 'before_event':
                date, sign = scheduler.calendar_event_id.start, -1
            else:
                date, sign = scheduler.calendar_event_id.stop, 1

            scheduler.scheduled_date = date + _INTERVALS[scheduler.interval_unit](sign * scheduler.interval_nbr) if date else False

    @api.model
    def cron_run(self):
        before_event = self.env["booking.mail.calendar"].search([("interval_type","=","before_event"),("scheduled_date", "<=", fields.Datetime.now()),("calendar_event_id.start", ">=", fields.Datetime.now()),("mail_done", "=", False)])
        after_event = self.env["booking.mail.calendar"].search([("interval_type","=","after_event"),("scheduled_date", "<=",fields.Datetime.now()),("calendar_event_id.stop", "<=", fields.Datetime.now()),("mail_done", "=", False)])
        after_sub = self.env["booking.mail.calendar"].search([("interval_type","=","after_sub"),("scheduled_date", "<=",fields.Datetime.now()),("interval_unit", "!=", "now"),("mail_done", "=", False)])

        booking_mail_calendar_ids = before_event + after_event + after_sub

        for booking_mail_calendar_id in booking_mail_calendar_ids:
            for partner_id in booking_mail_calendar_id.partner_ids:
                booking_mail_calendar_id._send_mail(partner_id)
                booking_mail_calendar_id.mail_count_done += 1 
            booking_mail_calendar_id.mail_done = True

    def _send_mail(self,partner_id):
        """ Mail action: send mail to attendees """
        if partner_id.email:
            author = partner_id
        elif partner_id.parent_id.email:
            author = partner_id.parent_id
        else:
            author = self.env.ref('base.user_root').partner_id

        composer_values = {
            'composition_mode': 'mass_mail',
            'force_send': False,
            'model': self._name,
            'record_name': False,
            'res_ids': [self.id],
            'template_id': self.template_ref.id,
        }
        # force author, as mailing mode does not try to find the author matching
        # email_from (done only when posting on chatter); give email_from if not
        # configured on template
        composer_values['author_id'] = author.id
        composer_values['email_from'] = self.template_ref.email_from or author.email_formatted
        composer = self.env['mail.compose.message'].create(composer_values)
        # backward compatible behavior: event mail scheduler does not force partner
        # creation, email_cc / email_to is kept on outgoing emails
        composer.with_context(mail_composer_force_partners=False)._action_send_mail()


    