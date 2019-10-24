# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Enterprise Management Solution, third party addon
#    Copyright (C) 2019 Vertel AB (<http://vertel.se>).
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
from odoo.exceptions import except_orm, Warning, RedirectWarning

import logging
_logger = logging.getLogger(__name__)



class parter_vcard(http.Controller):


    @http.route(['/vcard/<string:partner_name>','/partner/vc/<int:partner_id>'], type='http', auth="public", website=True, )
    def vcard_partner_view(self, partner_name=None,partner_id=None, **post):
        name = partner_name.replace(':.-_','    ')
        partner = request.env['res.partner'].search([('name','ilike',name)])  
        return request.render("partner_vcard.partner_vcard_view", {'partner':partner})
    
    @http.route([
        '/partner/<int:partner_id>/vcard.vcl',
    ], type='http', auth="public", website=False, )
    def vcard_partner(self, partner_id, **post):
        partner = request.env['res.partner'].sudo().browse(partner_id)
        return """BEGIN:VCARD
VERSION:3.0
FN;CHARSET=UTF-8:Melvin Helgesson
N;CHARSET=UTF-8:Helgesson;Melvin;;;
EMAIL;CHARSET=UTF-8;type=WORK,INTERNET:melvin.helgesson@izwop.com
PHOTO;TYPE=undefined:https://izwop-cdn.azureedge.net/izwop-com/melvin-helgesson/static/uploads/0 (6).jpeg
TEL;TYPE=WORK,VOICE:+46706123445
TITLE;CHARSET=UTF-8:VP Business Development
ORG;CHARSET=UTF-8:iZwop® 
URL;CHARSET=UTF-8:https://my.izwop.com/izwop-com/melvin-helgesson
REV:2019-09-13T09:26:53.011Z
END:VCARD""".format(name=partner.name,given_name=partner.name.split(' ')[0],family_name=partner.name.split(' ')[-1])

