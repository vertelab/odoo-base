from odoo import fields, models


class MailTrackingValue(models.Model):
    _inherit = 'mail.tracking.value'

    active = fields.Boolean(string="Active", default=True)