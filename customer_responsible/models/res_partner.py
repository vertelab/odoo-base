from odoo import models, fields, api, _

class Contacts(models.Model):
    _inherit = "res.partner"

    customer_responsible_id = fields.Many2one('res.users', string="Customer Responsible", domain=[('share', '=', False)])
