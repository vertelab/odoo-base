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
    office = fields.Many2one('res.partner.office', string="Office")
    work_phone = fields.Integer(string='Work phone', help="Work phone number")
    available_since = fields.Datetime(string='Available since', help="Time when they became available") #datetime/time?
    org_or_social_sec_nr = fields.Char(string='Organization/Social security number', help="Social security number or organization number")
    cfar = fields.Integer(string='CFAR', help="CFAR number")
    customer_nr = fields.Integer(string='Customer number', help="Customer number")

    office_code = fields.Integer(string='Office code', related='office.office_code')
    
    #office_code = fields.Integer(string="Office code") #bör tas från office och vara satt för office partners
    is_jobseeker = fields.Boolean(string="Jobseeker")
    is_independent_partner = fields.Boolean(string="Independent partner")
    is_government = fields.Boolean(string="Government")
    is_employer = fields.Boolean(string="Employer")

    #type = fields.Selection(selection_add=[('af office', 'AF Office')])



    

