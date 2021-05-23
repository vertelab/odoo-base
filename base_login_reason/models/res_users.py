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
import werkzeug
from datetime import datetime, timedelta
from odoo import SUPERUSER_ID
from odoo import fields, api, http
from odoo import models
from odoo.exceptions import AccessDenied
from odoo.http import request
from ..controllers.main import clear_session_history
from os.path import getmtime
from time import time
from os import utime
from odoo.http import SessionExpiredException

_logger = logging.getLogger(__name__)

class ResUsers(models.Model):

    _inherit = 'res.users'

    sid = fields.Char('Session ID')
    login_reason = fields.Text("Login Reason")
    session_length = fields.Integer("Session length")
    exp_date = fields.Datetime('Expiry Date')
    logged_in = fields.Boolean('Logged In')
    ticket_ID = fields.Char("Ticket ID")
    last_update = fields.Datetime(string="Last Connection Updated")
    
    def _clear_session(self):
        """
            Function for clearing the session details for user
        """
        self.write({'sid': False, 'exp_date': False, 'logged_in': False,
                    'last_update': datetime.now()})
    #
    def _save_session(self, minutes=120):
        """
            Function for saving session details to corresponding user
        """

        exp_date = datetime.utcnow() + timedelta(minutes=minutes)
        sid = request.httprequest.session.sid
        self.sudo().write({'sid': sid, 'exp_date': exp_date,
                                            'logged_in': True,
                                            'last_update': datetime.now()})
    #
    def validate_sessions_check_user(self, user):
        users = self.search([('exp_date', '!=', False),('id','=',user.id)])
        for user in users:
            if user.exp_date < datetime.utcnow():
                audit_log = self.env['base.login.reason'].sudo().search(
                    [('user_id', '=', user.id),('logged_out','=',False)])
                if audit_log:
                    audit_log.write({'logged_out':datetime.now(),'state':'logged_out'})
                    self._cr.commit()
                    user._clear_session()
                    request.session.logout(keep_db=True)
 

    @api.model_cr_context
    def _auth_timeout_get_ignored_urls(self):
        """Pluggable method for calculating ignored urls
        Defaults to stored config param
        """
        params = self.env['ir.config_parameter']
        return params._auth_timeout_get_parameter_ignored_urls()

    @api.model_cr_context
    def _auth_timeout_deadline_calculate(self, session_length):
        """Pluggable method for calculating timeout deadline
        Defaults to current time minus delay using delay stored as config
        param.
        """
        params = self.env['ir.config_parameter']
        delay = session_length
        if delay <= 0:
            return False
        return time() - delay

    @api.model_cr_context
    def _auth_timeout_session_terminate(self, session):
        """Pluggable method for terminating a timed-out session

        This is a late stage where a session timeout can be aborted.
        Useful if you want to do some heavy checking, as it won't be
        called unless the session inactivity deadline has been reached.

        Return:
            True: session terminated
            False: session timeout cancelled
        """
        if session.db and session.uid:
            session.logout(keep_db=True)
        return True

    @api.model_cr_context
    def _auth_timeout_check(self, session_length):
        """Perform session timeout validation and expire if needed."""
        if not http.request:
            return

        session = http.request.session

        # Calculate deadline
        deadline = self._auth_timeout_deadline_calculate(session_length)

        # Check if past deadline
        expired = False
        if deadline is not False:
            path = http.root.session_store.get_session_filename(session.sid)
            try:

                expired = getmtime(path) < deadline
            except OSError:
                _logger.exception(
                    'Exception reading session file modified time.',
                )
                # Force expire the session. Will be resolved with new session.
                expired = True

        # Try to terminate the session
        terminated = False
        if expired:
            terminated = self._auth_timeout_session_terminate(session)

        # If session terminated, all done
        if terminated:
            raise SessionExpiredException("Session expired")

        # Else, conditionally update session modified and access times
        ignored_urls = self._auth_timeout_get_ignored_urls()

        if http.request.httprequest.path not in ignored_urls:
            if 'path' not in locals():
                path = http.root.session_store.get_session_filename(
                    session.sid,
                )
            try:
                utime(path, None)
            except OSError:
                _logger.exception(
                    'Exception updating session file access/modified times.',
                )
