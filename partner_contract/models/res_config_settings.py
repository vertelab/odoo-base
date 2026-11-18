from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class ConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    active_paying_users = fields.Integer(compute="_compute_active_paying_users")

    @api.depends('company_id')
    def _compute_active_paying_users(self):
        res_users_count = self.env["res.users"].active_paying_users()
        for record in self:
            record.active_paying_users = res_users_count

    def action_active_paying_users(self):
        group = self.env.ref('base.group_user')
        res_users_ids = self.env["res.users"].search([("group_ids", "=", group.id), ("login", "!=", "admin")])
        action = {
            'name': 'Active Paying Users',
            'type': 'ir.actions.act_window',
            'res_model': 'res.users',
            'view_mode': 'list,kanban,form',
            'target': 'current',
            'domain': [("id", 'in', res_users_ids.ids)]
        }
        return action
