# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from collections import defaultdict
from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class RoleMassAdditionWizard(models.TransientModel):
    _name = 'role.mass.addition.wizard'
    _description = 'Adds multible users to one role'

    role_id = fields.Many2one(
        comodel_name='res.users.role',
        required=True,
        string='Role to assign'
    )

    def mass_add_users_to_role(self):
        ctx = self.env.context.get
        users = ctx('user_ids')
        for u in users:
            user = self.env['res.users'].browse(u)
            if user in self.role_id.line_ids.user_id:
                #TODO: Check that 'From' and 'To' are empty.
                _logger.warning("User %s is already part of %s", user.name, self.role_id.name)
                pass
            else:
                _logger.warning("User %s is added to %s", user.name, self.role_id.name)
                #new_line = self.env['res.users.role.line'].create()
                user.write({'role_line_ids': [(0, 0, {'user_id': user.id, 'role_id': self.role_id.id})]})
                

    def mass_remove_users_from_role(self):
        ctx = self.env.context.get
        users = ctx('user_ids')
        for u in users:
            user = self.env['res.users'].browse(u)
            if user in self.role_id.line_ids.user_id:
                #TODO: Check that 'From' and 'To' are empty.
                _logger.warning("User %s is removed from role %s", user.name, self.role_id.name)
                to_disable = self.env['res.users.role.line'].search([('user_id','=',user.id),('role_id','=',self.role_id.id)], limit=1)
                to_disable.unlink()
            else:
                _logger.warning("User %s is not in role %s", user.name, self.role_id.name)
                pass


class ResUsersRoleLine(models.Model):
    _inherit = 'res.users.role.line'

    @api.depends('role_id','role_id.name')
    def get_name_from_role(self):
        for record in self:
            record.name = record.role_id.name
            
    name = fields.Char(compute='get_name_from_role', store=True)
