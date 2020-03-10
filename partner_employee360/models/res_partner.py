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

from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = "res.partner" #odoo inheritance från res.partner
    #_name = ""
    office_name = fields.Char(string="Office", help="Office name")
    work_phone = fields.Char(string='Work phone', help="Work phone number")
    available_since = fields.Char(string='Available since', help="Time when they became available")
    org_or_social_sec_nr = fields.Char(string='Social security number', help="Social security number or organization number")
    cfar = fields.Char(string='CFAR', help="CFAR number")
    sni_code = fields.Char(string='SNI-code', help="SNI-code")
    customer_nr = fields.Char(string='Customer number', help="Customer number")



    

