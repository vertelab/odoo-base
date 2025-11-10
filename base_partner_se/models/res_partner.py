from odoo import models, fields, api, _


class BasePartner(models.Model):
    _inherit = 'res.partner'

    personal_number = fields.Char(string="Personal Number")
    temporary_personal_number = fields.Char(string="Temporary Personal Number")
    coordination_number = fields.Char(string="Coordination Number")