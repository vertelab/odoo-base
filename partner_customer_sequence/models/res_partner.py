from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def set_all_customers_number(self):
        partners = self.env['res.partner'].search([])
        _logger.warning(f"{partners=}")
        partners._set_costumer_number()

    def _set_costumer_number(self):
        for rec in self:
            if not rec.customer_sequence:
                sequence_code = self.env['ir.sequence'].next_by_code('res.partner')
                partner_id = self.env['res.partner'].search([('customer_sequence', '=', sequence_code)], limit=1)
                while partner_id:
                    sequence_code = self.env['ir.sequence'].next_by_code('res.partner')   
                    partner_id = self.env['res.partner'].search([('customer_sequence', '=', sequence_code)], limit=1)             
                rec.customer_sequence = sequence_code

    customer_sequence = fields.Char(string='Customer Number', readonly=True)
    our_customer_number = fields.Integer(string='Our Customer Number')
    company_code_partner = fields.Char(string='Legal Unit')

    @api.model
    def create(self, values):
        res = super(ResPartner, self).create(values)
        res._set_costumer_number()
        return res
