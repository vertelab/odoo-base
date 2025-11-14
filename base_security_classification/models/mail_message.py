from odoo import fields, models


class MailMessage(models.Model):
    _inherit = 'mail.message'

    active = fields.Boolean(string="Active", default=True)