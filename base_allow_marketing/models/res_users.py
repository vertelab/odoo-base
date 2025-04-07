from odoo import models, fields, api, _


class ResUsers(models.Model):
    _inherit = "res.users"

    allow_email_marketing = fields.Selection(
        related="partner_id.allow_email_marketing",
        string="Allow Marketing", readonly=False
    )
