# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution, third party addon
#    Copyright (C) 2004-2019 Vertel AB (<http://vertel.se>).
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
from odoo import http
from odoo.http import request
import werkzeug
import hashlib

import logging
_logger = logging.getLogger(__name__)


class WebsiteScreenpop(http.Controller):
    @http.route([
        '/opencustomerview'
    ], type='http', auth="public", website=False, csrf=False)
    def opencustomerview(self, **post):
        """
        personnummer=<12 tecken>
        signatur=<5 tecken>
        arendetyp=<tre tecken, t ex P92>
        kontaktid=<10 siffror, för uppföljning/loggning id i ACE>
        bankid=<OK/annat>
        datatime=yyyy-mm-dd-hh
        token= <sha1 hemlighet + yyyy-mm-dd-hh + personnummer>
        debug=True 
        
        P92 första planeringssamtal
        """
        _logger.warn('opencustomerview %s' % post)
        secret = request.env['ir.config_parameter'].sudo().get_param('partner_view_360.secret', 'hemligt')
        # ~ token = hashlib.sha1(secret + fields.DateTime.now().tostring[:13].replace(' ','-') + post.get('personnummer') ).hexdigest()
        token = hashlib.sha1((secret + post.get('datatime', '0000-00-00-00') + post.get('personnummer','20010203-1234') + post.get('bankid', 'None') ).encode('utf-8')).hexdigest()
        _logger.warn("\n\ntoken: %s" % token)
        if not token == post.get('token'):
            return request.render('partner_view_360.403', {'error': 'ERROR: Token missmatch','our_token': token, 'ext_token': post.get('token'), 'partner': None, 'action': None, 'url': None, 'post': post,'secret': secret})
        # ~ action = self.env['ir.actions.act_window'].for_xml_id('partner_view_360', 'action_jobseekers')
        action = request.env.ref('partner_view_360.action_jobseekers')
        _logger.warn("action: %s" % action)
        # ~ return action
        partner = request.env['res.partner'].sudo().search([('company_registry','=',post.get('personnummer','20010203-1234'))]) # not granted yet
        _logger.warn("partner: %s pnr: %s " % (partner, post.get('personnummer','20010203-1234')))
        if partner and len(partner) == 1:
            # if not partner._grant_jobseeker_access(post.get('reason','None'))
            #     return request.render('partner_view_360.403', {'error': 'ERROR: Could not grant access','our_token': token, 'ext_token': post.get('token'), 'partner': partner, 'action': action,'url': None,'post': post})
            #
            partner.eidentification = post.get('bankid')
            # ~ res_url = '/web?id=%s&action=%s&model=res.partner&view_type=form' % (partner.id if partner else 0,action.id if action else 0)
            res_url = '/web?id=%s&action=%s&model=res.partner&view_type=form#id=%s&active_id=40&model=res.partner&view_type=form' % (partner.id if partner else 0,action.id if action else 0,partner.id if partner else 0)
            #'/web?id=823&action=371&model=res.partner&active_id=39&model=res.partner&view_type=form&menu_id=252#id=823&active_id=40&model=res.partner&view_type=form&menu_id='
            _logger.warn("res_url: %s" % res_url)
            if post.get('debug'):
                return request.render('partner_view_360.403', {'message': 'Debug','our_token': token, 'ext_token': post.get('token'), 'partner': partner, 'action': action,'url': res_url, 'post': post,'secret': secret})
            return werkzeug.utils.redirect(res_url)
            # return werkzeug.utils.redirect('/web?id=%s&action=%s&model=res.partner&view_type=form' % (partner.id if partner else 0,action.id if action else 0))
        # ~ return werkzeug.utils.redirect('/web?debug=true#id=242&action=337&model=res.partner&view_type=form&menu_id=219')
        else:
            return request.render('partner_view_360.403', {'error': 'ERROR: No partner found', 'our_token': token, 'ext_token': post.get('token'), 'partner': partner, 'action': action, 'post': post,'secret': secret})



    @http.route([
        '/opencustomerviewtest'
    ], type='http', auth="public", website=False, csrf=False)
    def opencustomerviewtest(self, **post):
        """
        personnummer=<12 tecken>
        signatur=<5 tecken>
        arendetyp=<tre tecken, t ex P92>
        kontaktid=<10 siffror, för uppföljning/loggning id i ACE>
        bankid=<OK/annat>
        datatime=yyyy-mm-dd-hh
        token= <sha1 hemlighet + yyyy-mm-dd-hh + personnummer>
        debug=True 
        
        P92 första planeringssamtal
        """
        _logger.warn('opencustomerview %s' % post)
        secret = request.env['ir.config_parameter'].sudo().get_param('partner_view_360.secret', 'hemligt')
        # ~ token = hashlib.sha1(secret + fields.DateTime.now().tostring[:13].replace(' ','-') + post.get('personnummer') ).hexdigest()
        token = hashlib.sha1((secret + post.get('datatime', '0000-00-00-00') + post.get('personnummer','20010203-1234') + post.get('bankid', 'None') ).encode('utf-8')).hexdigest()
        _logger.warn("\n\ntoken: %s" % token)
        if not token == post.get('token'):
            return request.render('partner_view_360.403', {'error': 'ERROR: Token missmatch','our_token': token, 'ext_token': post.get('token'), 'partner': None, 'action': None, 'url': None, 'post': post,'secret': secret})
        # ~ action = self.env['ir.actions.act_window'].for_xml_id('partner_view_360', 'action_jobseekers')
        action = request.env.ref('partner_view_360.action_jobseekers')
        _logger.warn("action: %s" % action)
        # ~ return action
        partner = request.env['res.partner'].sudo().search([],limit=1) 
            # ~ res_url = '/web?id=%s&action=%s&model=res.partner&view_type=form' % (partner.id if partner else 0,action.id if action else 0)
        res_url = '/web?id=%s&action=%s&model=res.partner&view_type=form#id=%s&active_id=40&model=res.partner&view_type=form' % (partner.id if partner else 0,action.id if action else 0,partner.id if partner else 0)
        #'/web?id=823&action=371&model=res.partner&active_id=39&model=res.partner&view_type=form&menu_id=252#id=823&active_id=40&model=res.partner&view_type=form&menu_id='
        res_url = "/web#id=306&active_id=23&model=res.partner&view_type=form&menu_id=209"
        
        return werkzeug.utils.redirect(res_url)