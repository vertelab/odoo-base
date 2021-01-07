from odoo import models, fields

class Groups(models.Model):
    _inherit = 'res.groups'

    is_dafa = fields.Boolean(string='DAFA Group')