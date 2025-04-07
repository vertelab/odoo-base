from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    allow_email_marketing = fields.Selection([
        ('yes', 'Yes'), ('no', 'No')], string="Allow Marketing",
        readonly=False
    )


