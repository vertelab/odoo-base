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
from odoo.exceptions import ValidationError



class ResPartner(models.Model):
    _inherit = "res.partner"  # odoo inheritance från res.partner
    #_name = ""

    work_phone = fields.Char(string='Work phone', help="Work phone number")
    age = fields.Char(string="Age", compute="calculate_age")
    company_registry = fields.Char(
        string='Organization number', help="organization number")
    social_sec_nr = fields.Char(string="Social security number", related="company_registry")
    social_sec_nr_age = fields.Char(string="Social security number", compute="combine_social_sec_nr_age")
    cfar = fields.Char(string='CFAR', help="CFAR number")
    customer_id = fields.Char(string='Customer number', help="Customer number")
    eidentification = fields.Char(string='E-Identification', help="BankId or other e-identification done OK or other")

    # office selection field for partners connected to an office, my_office_code filled in by office_code for the office
    office = fields.Many2one('res.partner', string="Office")
    #office_ids = fields.Many2many('res.partner', relation='res_partner_office_partner_rel', column1='partner_id', column2='office_id', string='Offices')
    my_office_code = fields.Char(
        string='Office code', related='office.office_code')

    # adds af office as a type of partner
    type = fields.Selection(selection_add=[('af office', 'AF Office'), ('foreign address','Foreign Address'), ('given address','Given address'), ('visitation address','Visitation Address')])

    # office code for office type partners only
    office_code = fields.Char(string="Office code")

    is_jobseeker = fields.Boolean(string="Jobseeker")
    is_independent_partner = fields.Boolean(string="Independent partner")
    is_government = fields.Boolean(string="Government")
    is_employer = fields.Boolean(string="Employer")

    jobseeker_category = fields.Char(string="Jobseeker category") #egen modell?
    customer_since = fields.Datetime(string="Customer since")
    jobseeker_work = fields.Boolean(string="Work")
    deactualization_date = fields.Datetime(string="Date")
    deactualization_reason = fields.Char(string="Reason") #egen modell?
    foreign_country_of_work = fields.Char(string="When working in foreign country")
    deactualization_message = fields.Text(string="Message to jobseeker regarding deactualization")

    #registered_by = fields.Many2one(string="Registered by", comodel_name="res.users")
    registered_through = fields.Selection(selection=[('pdm','PDM'),('self service','Self service'),('local office','Local office')], string="Registered Through")
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

    segment_jobseeker = fields.Selection(string="Segment", selection=[('a','A'), ('b','B'), ('c1','C1'), ('c2','C2'), ('c3','C3')]) 
    segment_employer = fields.Selection(string="Segment", selection=[('including 1','Including 1'), ('including 2',' Including 2'), ('entry job','Entry job'), ('national agreement','National agreement'), ('employment subsidy','Employment subsidy')])

    @api.one
    def combine_social_sec_nr_age(self): #How to do the popup???
        if self.company_registry != False:
            self.social_sec_nr_age = _("%s (%s years old)") % (self.company_registry, self.age)
        else:
            self.social_sec_nr_age = ""
    @api.one
    def combine_state_name_code(self):
        self.state_name_code = "%s %s" % (self.state_id.name, self.state_id.code)
    
    @api.one
    @api.constrains('company_registry')
    def calculate_age(self):
        wrong_input = False
        today = date.today()
        social_sec = self.company_registry
        social_sec_stripped = ""
        if self.is_jobseeker and social_sec != False:
            social_sec_split = social_sec.split("-")
            if len(social_sec_split) > 1:
                if len(social_sec_split[1]) != 4 or len(social_sec_split) > 2:
                    wrong_input = True
                    _logger.error("Incorrectly formated social security number (company_registry)")
                social_sec_stripped = social_sec_split[0]
                if len(social_sec_stripped) != 8:
                    wrong_input = True
                    _logger.error("Social security number (company_registry) field lenght is incorrect, should be 12")
            elif len(social_sec_split) == 1:
                if len(social_sec_split[0]) == 10:
                    wrong_input = True
                    social_sec_stripped = social_sec_split[0][:6]
                elif len(social_sec_split[0]) == 12:
                    social_sec_stripped = social_sec_split[0][:8]
                    self.company_registry = "%s-%s" %(social_sec_stripped, social_sec_split[0][8:12])
                else:
                    wrong_input = True
                    _logger.error("Social security number (company_registry) field lenght is incorrect, should be 12")
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
                if today.year - date_of_birth.year < 18: #if social security numbers with 10 numbers are reallowed, change this to something more reasonable in case children are allowed to register
                    year = int("19"+yr)
                    try:
                        date_of_birth = date(year, month, day)
                    except:
                        wrong_input = True
                        _logger.error("Could not convert social security number (company_registry) to date")
            elif len(social_sec_stripped) == 8:
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
                if years > 67:
                    self.age = _("This person is too old, at %s years old") % years
                    _logger.error("A person older than 67 should not be in the system, a person is %s years old" % years)
                else:
                    self.age = years
                
            else: 
                #return {
                #'warning': {'title': "Warning", 'message': "What is this?"},
                #}
                self.social_sec_nr = ""
                self.age = ""
                raise ValidationError(_("Please input a correctly formated social security number"))
    @api.multi
    def close_view(self):
        return{
            'name': _("Search Partner"),
            'view_type': 'form',
            #'src_model': "res.partner",
            'res_model': "hr.employee.jobseeker.search.wizard",
            'view_id': False, #self.env.ref("partner_view_360.search_jobseeker_wizard").id,
            'view_mode':"form",
            #'target': "current", 
            #'key2': "client_action_multi",
            'type': 'ir.actions.act_window',
        }

