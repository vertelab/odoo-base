from odoo import models, api, fields, _


class Partner(models.Model):
    _inherit = 'res.partner'

    counterpart_id = fields.Many2one('res.partner.counterpart', string="CounterPart")
