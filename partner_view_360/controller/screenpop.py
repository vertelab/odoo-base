# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution, third party addon
#    Copyright (C) 2004-2020 Vertel AB (<http://vertel.se>).
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

from odoo import models, fields, api, _
from zeep.client import CachingClient
from zeep.helpers import serialize_object
from zeep import xsd


import logging
_logger = logging.getLogger(__name__)


class WebsiteScreenpop(http.Controller):
    
    
    
    @http.route(['/opencustomerview'], type='http', auth="public", website=True, csrf=False)
    def opencustomerview(self, **post):
        """
        personnummer=<12 tecken>, exklusive bindestreck. Ex: '200102031234'
        signatur=<5 tecken>
        arendetyp=<tre tecken, t ex P92>
        kontaktid=<10 siffror, för uppföljning/loggning id i ACE>
        bankid=<OK/annat>
        datatime=yyyy-mm-dd-hh
        token= <sha1 hemlighet + yyyy-mm-dd-hh + personnummer>
        debug=True 
        
        P92 första planeringssamtal
        Test-URL: http://afcrm-v12-afcrm-test.tocp.arbetsformedlingen.se/opencustomerview?personnummer=200002022382&signatur=admin&arendetyp=T99&kontaktid=1752211167&bankid=&token=43970fa88b3afdb0b021f34304f98c31973a145c&datatime=2020-09-11-09&reason=none
        """
        _logger.warn('opencustomerview %s' % post)
        secret = request.env['ir.config_parameter'].sudo().get_param('partner_view_360.secret', 'hemligt')
        # ~ token = hashlib.sha1(secret + fields.DateTime.now().tostring[:13].replace(' ','-') + post.get('personnummer') ).hexdigest()
        if request.env.user.login != post.get('signatur'):
            return request.render('partner_view_360.403', {'error': 'ERROR: Signature missmatch','signatur':post.get('signatur'),'partner': None, 'action': None, 'url': None, 'post': post,'secret': secret})

        token = hashlib.sha1((secret + post.get('datatime', '0000-00-00-00') + post.get('personnummer', '').replace('-', '') + post.get('bankid', 'None') ).encode('utf-8')).hexdigest()
        if not token == post.get('token'):
            return request.render('partner_view_360.403', {'error': 'ERROR: Token missmatch','our_token': token, 'ext_token': post.get('token'), 'partner': None, 'action': None, 'url': None, 'post': post,'secret': secret,'signatur':post.get('signatur')})

        pnr = post.get('personnummer', '')
        if pnr and not '-' in pnr:
            pnr = pnr[:8] + '-' + pnr[8:12]
        partner = request.env['res.partner'].sudo().search([('company_registry','=',pnr)]) # not granted yet
        
        if not partner:
            return request.render('partner_view_360.403', {'error': 'ERROR: No partner found', 'our_token': token, 'ext_token': post.get('token'), 'partner': partner, 'action': None, 'post': post,'secret': secret,'signatur':post.get('signatur')})
        elif partner and len(partner) == 1:
            action = request.env.ref('partner_view_360.action_jobseekers')
            partner.eidentification = post.get('bankid')
            res_url = '%s/web#id=%s&action=%s&model=res.partner&view_type=form' % (
                                                                request.env['ir.config_parameter'].sudo().get_param('web.base.url',''),
                                                                partner.id if partner else 0,
                                                                action.id if action else 0
                                                            )            
            if post.get('bankid') != 'OK':
                action_bankid = request.env.ref('hr_360_view.search_jobseeker_wizard')
                request.session['ssn'] = post.get('personnummer')
                res_url = '%s/web#id=&action=%s&model=hr.employee.jobseeker.search.wizard&view_type=form' % (
                                                                request.env['ir.config_parameter'].sudo().get_param('web.base.url',''),
                                                                action_bankid.id if action_bankid else 0)
                return werkzeug.utils.redirect(res_url)
           # ~ Grant temporary access to these jobseekers or set this user as responsible for the jobseeker            
            res = partner.escalate_jobseeker_access(post.get('arendetyp'), request.env.user)
            if res[0] != 250:  # OK
                return request.render('partner_view_360.403', {'error': 'ERROR: Escalate rights [%s] %s' % res, 'partner': partner, 'signatur':post.get('signatur')})
            if post.get('debug'):
                return request.render('partner_view_360.403', {'message': 'Debug','our_token': token, 'ext_token': post.get('token'), 'partner': partner, 'action': action,'url': res_url, 'post': post,'secret': secret})
            return werkzeug.utils.redirect(res_url)
        else:
            return request.render('partner_view_360.403', {'error': 'ERROR: More than one partner found', 'our_token': token, 'ext_token': post.get('token'), 'partner': partner, 'action': None, 'post': post,'secret': secret,'signatur':post.get('signatur')})


    @http.route(['/opencustomerview/bankid'], type='http', auth="public", website=True, csrf=False)
    def opencustomerview_bankid(self, **post):
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
        message = _('You have to initiate BankID-identification') 
        bankid = res = None       
        pnr = post.get('personnummer', '')
        if pnr and not '-' in pnr:
            pnr = pnr[:8] + '-' + pnr[8:12]
        partner = request.env['res.partner'].sudo().search([('company_registry','=',pnr)]) # not granted yet
        if post.get('bankid_init'):
            message = _('Initiating BankID-identification, try to authenticate')
            bankid = CachingClient(request.env['ir.config_parameter'].sudo().get_param('partner_view_360.bankid_wsdl', 'http://bhipws.arbetsformedlingen.se/Integrationspunkt/ws/mobiltbankidinterntjanst?wsdl'))  # create a Client instance
            res = bankid.service.MobiltBankIDInternTjanst(post.get('personnummer'))
        return request.render('partner_view_360.bankid', {
                    'partner': partner,
                    'token': post.get('token'),
                    'datatime': post.get('datatime'),
                    'signatur': post.get('signatur'),
                    'personnummer': post.get('personnummer'),
                    'arendetyp': post.get('arendetyp'),
                    'kontaktid': post.get('kontaktid'),
                    'bankid_soap': bankid,
                    'bankid_res': res,
                    })


    @http.route(['/opencustomerview/bankidtest'], type='http', auth="public", website=True, csrf=False)
    def opencustomerview_bankid(self, **post):
        """
        personnummer=<12 tecken>
        """
        bankid = res = None       
        pnr = post.get('personnummer', '')
        if pnr and not '-' in pnr:
            pnr = pnr[:8] + '-' + pnr[8:12]
        message = _('Initiating BankID-identification, try to authenticate')
        bankid = CachingClient(request.env['ir.config_parameter'].sudo().get_param('partner_view_360.bankid_wsdl', 'http://bhipws.arbetsformedlingen.se/Integrationspunkt/ws/mobiltbankidinterntjanst?wsdl'))  # create a Client instance
        res = bankid.service.MobiltBankIDInternTjanst(post.get('personnummer'))
        return request.render('partner_view_360.bankid', {
                    'personnummer': post.get('personnummer'),
                    'bankid_soap': bankid,
                    'bankid_res': res,
                    })
                
        
    @http.route(['/opencustomerview/bankidtest'], type='http', auth="public", website=True, csrf=False)
    def opencustomerview_bankidtest(self, **post):
        """
        personnummer=<12 tecken>
        """
        bankid = res = None       
        pnr = post.get('personnummer', '')
        if pnr and not '-' in pnr:
            pnr = pnr[:8] + '-' + pnr[8:12]
        message = _('Initiating BankID-identification, try to authenticate')
        bankid = CachingClient(request.env['ir.config_parameter'].sudo().get_param('partner_view_360.bankid_wsdl', 'http://bhipws.arbetsformedlingen.se/Integrationspunkt/ws/mobiltbankidinterntjanst?wsdl'))  # create a Client instance
        res = bankid.service.MobiltBankIDInternTjanst(post.get('personnummer'),'crm')
        if res.get('orderRef'):
            res = bankid.service.verifieraIdentifiering(res['orderRef'],'crm')
        return request.render('partner_view_360.bankid', {
                    'personnummer': post.get('personnummer'),
                    'bankid_soap': bankid,
                    'bankid_res': res,
                    })
                
        
    @http.route(['/opencustomerviewtest'], type='http', auth="public", website=True, csrf=False)
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
        token = hashlib.sha1((secret + post.get('datatime', '0000-00-00-00') + post.get('personnummer','20010203-1234') + post.get('bankid', '') ).encode('utf-8')).hexdigest().upper()
        _logger.warn("\n\ntoken: %s" % token)
        if not token == post.get('token').upper():
            return request.render('partner_view_360.403', {'error': 'ERROR: Token missmatch','our_token': token, 'ext_token': post.get('token'), 'partner': None, 'action': None, 'url': None, 'post': post,'secret': secret})
        # ~ action = self.env['ir.actions.act_window'].for_xml_id('partner_view_360', 'action_jobseekers')
        action = request.env.ref('partner_view_360.action_screenpopup')
        _logger.warn("action: %s" % action)
        # ~ return action
        partner = request.env['res.partner'].sudo().search([],limit=1) 
            # ~ res_url = '/web?id=%s&action=%s&model=res.partner&view_type=form' % (partner.id if partner else 0,action.id if action else 0)
        res_url = '/web?id=%s&action=%s&model=res.partner&view_type=form#id=%s&active_id=40&model=res.partner&view_type=form' % (partner.id if partner else 0,action.id if action else 0,partner.id if partner else 0)
        #'/web?id=823&action=371&model=res.partner&active_id=39&model=res.partner&view_type=form&menu_id=252#id=823&active_id=40&model=res.partner&view_type=form&menu_id='
        res_url = "/web#id=306&active_id=23&model=res.partner&view_type=form&menu_id=209"
        
        return werkzeug.utils.redirect(res_url)

    @http.route(['/opencustomerviewt2'], type='http', auth="public", website=True, csrf=False)
    def opencustomerviewt2(self, **post):
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
        
        action = request.env.ref('partner_view_360.action_screenpopup')
        partner = request.env['res.partner'].sudo().search([('company_registry','=',post.get('personnummer','20010203-1234'))]) 
        secret = request.env['ir.config_parameter'].sudo().get_param('partner_view_360.secret', 'hemligt')
        token = hashlib.sha1((secret + post.get('datatime', '0000-00-00-00') + post.get('personnummer','20010203-1234') + post.get('bankid', '') ).encode('utf-8')).hexdigest()
        token1 = hashlib.sha1((secret + post.get('datatime', '0000-00-00-00') + post.get('personnummer','20010203-1234') + post.get('bankid', '') ).encode('utf-8')).hexdigest().upper()

        return request.render('partner_view_360.403', {'error': 'ERROR: No partner found', 'our_token': token, 'our_token1': token1, 'ext_token': post.get('token'), 'partner': partner, 'action': action, 'post': post,'secret': secret})
