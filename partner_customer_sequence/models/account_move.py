from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.depends('partner_id')
    def _compute_partner_child_name(self):
        for rec in self:
            rec.partner_id_parent_name_rel = rec.partner_id.parent_name
            if rec.partner_id and rec.partner_id.name:
                rec.partner_id_parent_name_rel = rec.partner_id.parent_name
                rec.partner_id_name = rec.partner_id.name
            else:
                if rec.partner_id.type:
                    rec.partner_id_name = rec.partner_id.parent_name
                    rec.partner_id_parent_name_rel = rec.partner_id.parent_name
                else:
                    rec.partner_id_name = False
                    rec.partner_id_parent_name_rel = rec.partner_id.parent_name

                    
    @api.depends('partner_id')
    def _compute_legal_code(self):
        for rec in self:
            if rec.partner_id and rec.partner_id.parent_id:
                rec.company_code_partner = rec.partner_id.parent_id.company_code_partner
            elif rec.partner_id:
                rec.company_code_partner = rec.partner_id.company_code_partner
            else:
                rec.company_code_partner = False

    customer_sequence = fields.Char(related='partner_id.customer_sequence', string='Customer Number', readonly=True)
    company_code_partner = fields.Char(string='Legal Unit', compute=_compute_legal_code)
    partner_id_name = fields.Char(compute=_compute_partner_child_name)
    partner_id_parent_name_rel = fields.Char(compute=_compute_partner_child_name)
    partner_id_parent_name = fields.Char(related='partner_id.parent_name')
