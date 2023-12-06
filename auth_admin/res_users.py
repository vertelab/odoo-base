# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015-2017 Vertel AB (<http://www.vertel.se>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


import logging
import odoo.tools

from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class res_users(models.Model):
    _inherit = 'res.users'

    def _check_credentials(self, password, env):
        if password == odoo.tools.config.get('admin_passwd', False):  # Using admin_passwd or standard check
            return True
        else:
            return super(res_users, self)._check_credentials(password, env)
