from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.depends('partner_id')
    def _compute_partner_child_name(self):
        for rec in self:
            if rec.partner_id and rec.partner_id.name:
                rec.partner_id_name = rec.partner_id.name
            else:
                if rec.partner_id.type:
                    rec.partner_id_name = rec.partner_id.type.capitalize() + " Address"
                else:
                    rec.partner_id_name = False

    customer_sequence = fields.Char(related='partner_id.customer_sequence', string='Customer Number', readonly=True)
    company_code_partner = fields.Char(related='partner_id.company_code_partner', string='Legal Unit')
    partner_id_name = fields.Char(compute=_compute_partner_child_name)
    partner_id_name_rel = fields.Char(related='partner_id_name')
    partner_id_parent_name = fields.Char(related='partner_id.parent_name')
