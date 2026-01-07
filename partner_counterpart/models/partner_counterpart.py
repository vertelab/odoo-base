from odoo import models, api, fields, _


class PartnerCounterPart(models.Model):
    _name = 'res.partner.counterpart'
    _description = 'Partner Counterpart'

    name = fields.Char(string="Name")
    code = fields.Char(string="Code")
    partner_id = fields.Many2one('res.partner', string='Partner')
