from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class Users(models.Model):
    _inherit = 'res.users'

    @api.model
    def active_paying_users(self):
        group = self.env.ref('base.group_user')
        # #if VERSION >= "19.0"
        res_users_count = self.env["res.users"].search_count([("group_ids", "=", group.id), ("login", "!=", "admin")])
        # #else
        res_users_count = self.env["res.users"].search_count([("groups_id", "=", group.id), ("login", "!=", "admin")])
        # #endif
        return res_users_count
