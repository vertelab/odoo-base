import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError

_logger = logging.getLogger(__name__)

class Partner(models.Model):
    _inherit = 'res.partner'

    is_template = fields.Boolean()

    def create_partner_from_template(self):
        copy = self.copy()
        return {
            'type': 'ir.actions.act_window',
            'name': 'New Copy',
            'res_model': 'res.partner', 
            'view_mode': 'form',
            'res_id': copy.id,         
            'target': 'current', 
        }
