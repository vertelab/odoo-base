 #-*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2019- Vertel AB.
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
from openerp import models, fields, api, _
from openerp.exceptions import Warning
from openerp import SUPERUSER_ID
from openerp import http
from openerp.http import request
import random

import logging
_logger = logging.getLogger(__name__)


class res_partner_sudo_login_url(models.TransientModel):
    _name = 'res.partner.sudo.login.url'

    sudo_login_url = fields.Char(string='Sudo Login url', help='Copy the link above to an incognito window or a new web browser to login.', readonly=True)


class res_partner(models.Model):
    _inherit = 'res.partner'

    hide_for_employee = fields.Boolean(compute='_hide_for_employee')

    @api.one
    def _hide_for_employee(self):
        user = self._find_user()
        
        # check if we found anything
        if not user:
            self.hide_for_employee = True
        else:
            employee = self.env['hr.employee'].search([('user_id.partner_id', '=', self.id)])
            self.hide_for_employee = True if employee else False
            
    @api.multi
    def _find_user(self):
        # try to find user for partner.
        user = self.env['res.users'].search([('partner_id', '=', self.id)])
        if not user:
            # try again, this time looking at partners parents
            user = self.env['res.users'].search([('partner_id.parent_id', '=', self.id)], limit=1)
        return user

    @api.multi
    def sudo_login(self):
        self.ensure_one()
        user = self._find_user()
        if not user:
            raise Warning(_('Need a user for login'))
        user.sudo_pw = '%032x' % random.getrandbits(256)
        return {
            'type': 'ir.actions.act_url',
            # ~ 'url': '/sudo_login_as?user_id=%s&login=%s&password=%s' %(self.sudo_id.id, self.sudo_id.login, self.sudo_id.sudo_pw),
            'url': '/sudo_login_as?user_id=%s&login=%s&password=%s' %(user.id, user.login, user.sudo_pw),
            'target': 'new',
        }

    @api.multi
    def sudo_login_url(self):
        self.ensure_one()
        user = self._find_user()
        if not user:
            raise Warning(_('Need a user for login'))
        user.sudo_pw = '%032x' % random.getrandbits(256)
        sudo_login_url = '%s/sudo_login_as_url?db=%s&login=%s&password=%s' %(
                self.env['ir.config_parameter'].get_param('web.base.url'),
                http.db_list()[0],
                user.login,
                user.sudo_pw,
            )
        url_obj = self.env['res.partner.sudo.login.url'].create({'sudo_login_url': sudo_login_url})
        return {
            'name': _('Sudo Login URL'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'res.partner.sudo.login.url',
            'res_id': url_obj.id,
            'view_id': self.env.ref('res_partner_sudo_login.sudo_login_url_form').id,
            'target': 'new',
            'context': {},
        }


class res_users(models.Model):
    _inherit = 'res.users'

    sudo_pw = fields.Char()

    def check_credentials(self, cr, uid, password):
        user = self.search(cr, SUPERUSER_ID, [('partner_id', '=', uid),('sudo_pw' ,'=', password)])
        if user:
            return True
        return super(res_users, self).check_credentials(cr, uid, password)


class MainController(http.Controller):

    @http.route('/sudo_login_as', type='http', auth='user', website=True)
    def sudo_login_as(self, **post):
        if request.params['user_id'] and request.params['login'] and request.params['password']:
            user = request.env['res.users'].sudo().browse(int(request.params['user_id']))
            request.session['context']['lang'] = user.lang
            request.session['context']['uid'] = user.id
            request.session['uid'] = user.id
            request.session['login'] = request.params['login']
            request.session['password'] = request.params['password']
            return http.redirect_with_hash('/')

    @http.route('/sudo_login_as_url', type='http', auth='public', website=True)
    def sudo_login_as_url(self, **post):
        if request.params['db'] and request.params['login'] and request.params['password']:
            return request.render('web.login', {'db': request.params['db'] ,'login': request.params['login'], 'password': request.params['password']})


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
