from odoo import models, fields, api, _


class Company(models.Model):
    _inherit = "res.company"

    fiscal_position_id = fields.Many2one("account.fiscal.position", string="Fiscal Position")
