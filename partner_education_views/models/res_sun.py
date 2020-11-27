from odoo import models, fields


class ResSun(models.Model):
    _name = 'res.sun'

    partner_ids = fields.Many2many(comodel_name="res.partner")

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Official Code',
                       help="Official code, group, sub-group or detail group.")
    description = fields.Char(string='Description')
    parent_id = fields.Many2one(comodel_name='res.sun', string='Parent')
