from odoo import models, fields, api, _

class ResPartner(models.Model):
    _inherit = 'res.partner'

    customer_sequence = fields.Char(string='Sequence', readonly=True)

    @api.model
    def create(self, values):
        res = super(ResPartner, self).create(values)        
        if res.customer_rank > 0 and not res.customer_sequence:
            res.customer_sequence = self.env['ir.sequence'].next_by_code('res.partner')
                
        return res

    
    def write(self, values):
        res = super(ResPartner, self).write(values)
        if self.customer_rank and not self.customer_sequence:
            self.customer_sequence = self.env['ir.sequence'].next_by_code('res.partner')
        return res
