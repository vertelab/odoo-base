from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def set_all_customers_number(self):
        _logger.warning("set_all_customers_number" * 100)
        partners = self.env['res.partner'].search([])
        _logger.warning(f"{partners=}")
        partners._set_costumer_number()

    def _set_costumer_number(self):
        for rec in self:
            if not rec.customer_sequence:
                rec.customer_sequence = self.env['ir.sequence'].next_by_code('res.partner')

    customer_sequence = fields.Char(string='Customer Number', readonly=True)

    our_customer_number = fields.Integer(string='Our Customer Number')

    @api.model
    def create(self, values):
        res = super(ResPartner, self).create(values)
        if not res.customer_sequence:
            res.customer_sequence = self.env['ir.sequence'].next_by_code('res.partner')
        return res
