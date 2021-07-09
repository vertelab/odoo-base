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

import os
import werkzeug
import werkzeug.contrib.sessions
import werkzeug.datastructures
import werkzeug.exceptions
import werkzeug.local
import werkzeug.routing
import werkzeug.wrappers
import werkzeug.wsgi
from odoo.addons.web.controllers import main
import odoo
import odoo.modules.registry
from odoo import SUPERUSER_ID
from odoo import http
from odoo.exceptions import AccessError
from odoo.http import Response
from odoo.http import request
from odoo.service import security
from odoo.tools.translate import _
from datetime import datetime

def clear_session_history(u_sid, f_uid=False):
    """ Clear all the user session histories for a particular user """
    path = odoo.tools.config.session_dir
    store = werkzeug.contrib.sessions.FilesystemSessionStore(
        path, session_class=odoo.http.OpenERPSession, renew_missing=True)
    session_fname = store.get_session_filename(u_sid)
    try:
        os.remove(session_fname)
        return True
    except OSError:
        pass
    return False

def super_clear_all():
    """ Clear all the user session histories """
    path = odoo.tools.config.session_dir
    store = werkzeug.contrib.sessions.FilesystemSessionStore(
        path, session_class=odoo.http.OpenERPSession, renew_missing=True)
    for fname in os.listdir(store.path):
        path = os.path.join(store.path, fname)
        try:
            os.unlink(path)
        except OSError:
            pass
    return True

class Home(main.Home):

    @http.route('/web/login', type='http', auth="none", sitemap=False)
    def web_login(self, redirect=None, **kw):
        result = super(Home, self).web_login(redirect=redirect, kw=kw)
        if kw.get('login_reason') and kw.get('session_length') and kw.get('ticket_ID'):
            log = request.env['res.users.log'].create({})
            session_ID = request.session.sid
            user = request.env['res.users'].browse(request.session.uid)
            request.env['base.login.reason'].create(
                {'user_id': request.session.uid, 'logged_in': log.create_date, 'session_ID': session_ID,
                 'login_reason': kw.get('login_reason'), 'state': 'logged_in',
                 'ticket_ID': kw.get('ticket_ID'), 'length':kw.get('session_length')})
            user._save_session(int(kw.get('session_length')))
        return result

class Session(main.Session):

    @http.route('/web/session/logout', type='http', auth="none")
    def logout(self, redirect='/web'):
        
        audit_log = request.env['base.login.reason'].sudo().search(
            [('user_id', '=', request.session.uid),('logged_out','=',False)], limit=1)
        if audit_log:
            audit_log.logged_out = datetime.now()
            audit_log.state = 'logged_out'
        user = request.env['res.users'].sudo().search(
            [('id', '=', request.session.uid)])
        # clear user session
        user._clear_session()
        request.session.logout(keep_db=True)
        print ("Completed the function...")
        return werkzeug.utils.redirect(redirect, 303)

    @http.route('/clear_all_sessions', type='http', auth="none")
    def logout_all(self, redirect='/web', f_uid=False):
        """ Log out from all the sessions of the current user """
        
        if f_uid:
            user = request.env['res.users'].with_user(1).browse(int(f_uid))
            if user:
                # clear session session file for the user
                session_cleared = clear_session_history(user.sid, f_uid)
                if session_cleared:
                    # clear user session
                    user._clear_session()
        request.session.logout(keep_db=True)
        return werkzeug.utils.redirect(redirect, 303)

    @http.route('/super/logout_all', type='http', auth="none")
    def super_logout_all(self, redirect='/web'):
        """ Log out from all the sessions of all the users """
        users = request.env['res.users'].with_user(1).search([])
        for user in users:
            # clear session session file for the user
            session_cleared = super_clear_all()
            if session_cleared:
                # clear user session
                user._clear_session()
        request.session.logout(keep_db=True)
        return werkzeug.utils.redirect(redirect, 303)
