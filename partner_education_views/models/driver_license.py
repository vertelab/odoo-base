from odoo import models, fields


class ResDriversLicense(models.Model):
    _name = 'res.drivers_license'

    partner_id = fields.Many2one(comodel_name="res.partner")
    name = fields.Char(string='Class', required=True)  # A,B etc.
    description = fields.Char(string='Description')
