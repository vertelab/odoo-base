# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution, third party addon
#    Copyright (C) 2004-2021 Vertel AB (<http://vertel.se>).
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
from datetime import datetime, timedelta
from odoo import SUPERUSER_ID
from odoo import fields, api
from odoo import models
from odoo.exceptions import AccessDenied
from odoo.http import request
from ..controllers.main import clear_session_history

_logger = logging.getLogger(__name__)

class ResUsers(models.Model):

    _inherit = 'res.users'

    sid = fields.Char('Session ID')
    login_reason = fields.Text("Login Reason")
    session_length = fields.Integer("Session length")
    exp_date = fields.Datetime('Expiry Date')
    logged_in = fields.Boolean('Logged In')
    last_update = fields.Datetime(string="Last Connection Updated")

    # Method call when user login, create history record here
    @api.model
    def _update_last_login(self):
        log = self.env['res.users.log'].create({})
        session_ID = request.session.sid
        self.env['base.login.reason'].create(
            {'user_id': self.id, 'logged_in': log.create_date, 'session_ID':session_ID,
             'login_reason':self.login_reason, 'state':'audit'})


    def _clear_session(self):
        """
            Function for clearing the session details for user
        """
        self.write({'sid': False, 'exp_date': False, 'logged_in': False,
                    'last_update': datetime.now()})
    #
    def _save_session(self):
        """
            Function for saving session details to corresponding user
        """
        exp_date = datetime.utcnow() + timedelta(minutes=45)
        sid = request.httprequest.session.sid
        self.with_user(SUPERUSER_ID).write({'sid': sid, 'exp_date': exp_date,
                                            'logged_in': True,
                                            'last_update': datetime.now()})
    #
    def validate_sessions(self):
        """
            Function for validating user sessions
        """
        users = self.search([('exp_date', '!=', False)])
        for user in users:
            if user.exp_date < datetime.utcnow():
                # clear session session file for the user
                session_cleared = clear_session_history(user.sid)
                if session_cleared:
                    # clear user session
                    user._clear_session()
                    _logger.info("Cron _validate_session: "
                                 "cleared session user: %s" % (user.name))
                else:
                    _logger.info("Cron _validate_session: failed to "
                                 "clear session user: %s" % (user.name))
