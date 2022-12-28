# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    def _verify_sftp_user(self, password):
        assert password
        self.env.cr.execute(
            "SELECT COALESCE(password, '') FROM res_users WHERE id=%s",
            [self.env.user.id]
        )
        [hashed] = self.env.cr.fetchone()
        valid, replacement = self._crypt_context().verify_and_update(password, hashed)
        return valid
