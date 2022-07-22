from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    @api.model
    def set_all_customers_number(self):
        _logger.warning("set_all_customers_number"*100)
        partners = self.env['res.partner'].search([('customer_rank','>',0)])
        _logger.warning(f"{partners=}")
        partners._set_costumer_number()
    
    def _set_costumer_number(self):
        for rec in self:
            if rec.customer_rank > 0 and not rec.customer_sequence:
               rec.customer_sequence = self.env['ir.sequence'].next_by_code('res.partner')

    customer_sequence = fields.Char(string='Customer Number', readonly=True)

    our_customer_number = fields.Integer(string='Our Customer Number')
    
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
        
        # ~ def _default_description(self):
            # ~ return self.env['ir.ui.view']._render_template('event.event_default_descripton')

        # ~ description = fields.Html(string='Description', translate=html_translate, sanitize_attributes=False, sanitize_form=False, default=_default_description)
