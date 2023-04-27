from urllib import request
from odoo import api, fields, models
import requests
import logging
import json

_logger = logging.getLogger("dmitri")

class InvoiceFix(models.Model):
    _inherit = 'res.partner'

    def _invoice_total(self):
        self.total_invoiced = 0
        if not self.ids:
            return True

        all_partners_and_children = {}
        all_partner_ids = []
        for partner in self.filtered('id'):
            # price_total is in the company currency
            all_partners_and_children[partner] = self.with_context(active_test=False).search([('id', 'child_of', partner.id)]).ids
            all_partner_ids += all_partners_and_children[partner]
        

        domain = [
            ('partner_id', 'in', all_partner_ids),
            ('state', 'not in', ['draft', 'cancel']),
            ('move_type', 'in', ('out_invoice', 'out_refund')),
        ]
        price_totals = self.env['account.move'].search_read(domain, ['amount_total', 'partner_id'])
        for partner, child_ids in all_partners_and_children.items():
            partner.total_invoiced = sum(price['amount_total'] for price in price_totals if price['partner_id'] in child_ids)        




