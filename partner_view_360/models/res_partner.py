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
from datetime import date
_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"  # odoo inheritance från res.partner
    #_name = ""

    work_phone = fields.Integer(string='Work phone', help="Work phone number")
    age = fields.Char(string="Age", compute="calculate_age")
    company_registry = fields.Char(
        string='Organization number', help="organization number")
    cfar = fields.Char(string='CFAR', help="CFAR number")
    customer_id = fields.Char(string='Customer number', help="Customer number")

    # office selection field for partners connected to an office, my_office_code filled in by office_code for the office
    office = fields.Many2one('res.partner', string="Office")
    my_office_code = fields.Char(
        string='Office code', related='office.office_code')

    # adds af office as a type of partner
    type = fields.Selection(selection_add=[('af office', 'AF Office'), ('legal address','Legal Address'), ('foreign address','Foreign Address'), ('postal address','Postal Address')])

    # office code for office type partners only
    office_code = fields.Char(string="Office code")

    is_jobseeker = fields.Boolean(string="Jobseeker")
    is_independent_partner = fields.Boolean(string="Independent partner")
    is_government = fields.Boolean(string="Government")
    is_employer = fields.Boolean(string="Employer")

    jobseeker_category = fields.Char(string="Jobseeker category") #egen modell?
    customer_since = fields.Datetime(string="Since")
    jobseeker_work = fields.Boolean(string="Work")
    deactualization_date = fields.Datetime(string="Date")
    deactualization_reason = fields.Char(string="Reason") #egen modell?
    foreign_country_of_work = fields.Char(string="When working in foreign country")
    deactualization_message = fields.Text(string="Message to jobseeker regarding deactualization")

    state_statecode = fields.Char(compute="combine_state_statecode")

    registered_through = fields.Char(string="Registered Through")
    share_info_with_employers = fields.Boolean(string="Share name and address with employers")
    sms_reminders = fields.Boolean(string="SMS reminders")
    postal_address_id = fields.Many2one('res.partner', string="Postal address")
    postal_address_street = fields.Char(string="Postal address", related="postal_address_id.street")
    postal_address_zip = fields.Char(related="postal_address_id.zip")
    postal_address_city = fields.Char(related="postal_address_id.city")

    #def combine_state_statecode(self):
        

    def calculate_age(self):
        wrong_input = False
        today = date.today()
        if len(self.company_registry.split("-")[1]) != 4:
            wrong_input = True
            _logger.error("Incorrectly formated social security number (company_registry)")
        social_sec_stripped = self.company_registry[:-4]
        social_sec_stripped = social_sec_stripped.split("-")[0]
        date_of_birth = date(1980,1,1)
        if len(social_sec_stripped) == 6:
            yr = social_sec_stripped[:2]
            year = int("20"+yr)
            month = int(social_sec_stripped[2:4])
            day = int(social_sec_stripped[4:6])
            try:
                date_of_birth = date(year, month, day)
            except:
                wrong_input = True
                _logger.error("Could not convert social security number (company_registry) to date")
            if today.year - date_of_birth.year < 18:
                year = int("19"+yr)
                try:
                    date_of_birth = date(year, month, day)
                except:
                    wrong_input = True
                    _logger.error("Could not convert social security number (company_registry) to date")
    
        elif len(social_sec_stripped) > 6:
            try:
                date_of_birth = date(int(social_sec_stripped[:4]),int(social_sec_stripped[4:6]),int(social_sec_stripped[6:8]))
            except:
                wrong_input = True
                _logger.error("Could not convert social security number (company_registry) to date")
        else: 
            wrong_input = True
            _logger.error("Incorrectly formated social security number (company_registry)")
        
        if not wrong_input:
            years = today.year - date_of_birth.year
            if today.month < date_of_birth.month or (today.month == date_of_birth.month and today.day < date_of_birth.day):
                years -= 1
            self.age = years
        else: 
            self.age = "Error calculating age"