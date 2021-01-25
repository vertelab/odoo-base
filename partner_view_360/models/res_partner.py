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

from odoo import models, fields, api, _
import logging
import threading
import base64
from odoo.modules import get_module_resource
from datetime import date
_logger = logging.getLogger(__name__)
from odoo.exceptions import ValidationError
from odoo.tools import image_resize_image_big, image_colorize


class ResPartner(models.Model):
    _inherit = "res.partner"  
    _rec_name = "name_ssn"

    work_phone = fields.Char(string='Work phone', help="Work phone number")
    cfar = fields.Char(string='CFAR', help="CFAR number")
    customer_id = fields.Char(string='Customer number', help="Customer number")
    eidentification = fields.Char(string='E-Identification', help="BankId or other e-identification done OK or other")

    type = fields.Selection(selection_add=[('foreign address','Foreign Address'), ('given address','Given address'), ('visitation address','Visitation Address'), ('mailing address', 'Mailing Address')])
    
    is_jobseeker = fields.Boolean(string="Jobseeker")
    is_independent_partner = fields.Boolean(string="Independent partner")
    is_government = fields.Boolean(string="Government")
    is_employer = fields.Boolean(string="Employer")

    jobseeker_category_id = fields.Many2one(comodel_name='res.partner.skat')
    jobseeker_category = fields.Char(string="Jobseeker category", compute="combine_category_name_code")
    customer_since = fields.Datetime(string="Customer since")
    jobseeker_work = fields.Boolean(string="Work")
    deactualization_date = fields.Datetime(string="Date")
    deactualization_reason = fields.Char(string="Reason") #egen modell?
    foreign_country_of_work = fields.Char(string="When working in foreign country")
    deactualization_message = fields.Text(string="Message to jobseeker regarding deactualization")

    #registered_by = fields.Many2one(string="Registered by", comodel_name="res.users")
    registered_through = fields.Selection(selection=[('pdm','PDM'),('self service','Self service'), ('local office','Local office')], string="Registered Through")
    match_area = fields.Boolean(string="Match Area")
    share_info_with_employers = fields.Boolean(string="Share name and address with employers")
    sms_reminders = fields.Boolean(string="SMS reminders")
    visitation_address_id = fields.Many2one('res.partner', string="Visitation address")

    given_address_id = fields.Many2one('res.partner', string="given address")
    given_address_street = fields.Char(string="given address", related="given_address_id.street")
    given_address_zip = fields.Char(related="given_address_id.zip")
    given_address_city = fields.Char(related="given_address_id.city")
    employer_class = fields.Selection(selection=[('1','1'), ('2','2'), ('3','3'), ('4','4')])

    state_code = fields.Char(string="State code", related="state_id.code")
    state_name_code = fields.Char(string="Municipality", compute="combine_state_name_code")

    temp_officer_id = fields.Many2many(comodel_name='res.users', relation='res_partner_temp_officer_rel', string='Temporary Officers')

    segment_jobseeker = fields.Selection(string="Jobseeker segment", selection=[('a','A'), ('b','B'), ('c1','C1'), ('c2','C2'), ('c3','C3')]) 
    segment_employer = fields.Selection(string="Employer segment", selection=[('including 1','Including 1'), ('including 2',' Including 2'), ('entry job','Entry job'), ('national agreement','National agreement'), ('employment subsidy','Employment subsidy')])

    name_ssn = fields.Char(compute="_compute_name_ssn", store=True)
    
    communication_channel = fields.Selection([
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('letter', 'Letter')
    ])

    _sql_constraints = [
        ('customer_id_unique', 
        'UNIQUE(customer_id)',
        'customer_id field needs to be unique'
        )]

    @api.one
    def combine_state_name_code(self):
        self.state_name_code = "%s %s" % (self.state_id.name, self.state_id.code)

    @api.one
    def combine_category_name_code(self):
        self.jobseeker_category = "%s %s" % (self.jobseeker_category_id.name, self.jobseeker_category_id.code)

    def update_name_ssn(self):
        for partner in self:
            name = partner.name
            if partner.social_sec_nr:
                name += " " + partner.social_sec_nr
            partner.name_ssn = name
            partner.name = partner.name

    @api.depends("name", "social_sec_nr")
    def _compute_name_ssn(self):
        for partner in self:
            name = partner.name
            if partner.social_sec_nr:
                name += " " + partner.social_sec_nr
            partner.name_ssn = name