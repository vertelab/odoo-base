# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from collections import defaultdict
from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    def _action_role_mass_addition_wizard(self):
        user_ids = []
        for s in self:
            user_ids.append(s.id)
        return {'type': 'ir.actions.act_window',
           'name': _('Wizard Test'),
           'res_model': 'role.mass.addition.wizard',
           'target': 'new',
           'view_id': self.env.ref('base_user_role_mass_addition.role_mass_addition_wizard').id,
           'view_mode': 'form',
           'context': {'user_ids': user_ids}
           }
