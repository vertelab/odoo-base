# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution, third party addon
#    Copyright (C) 2004-2017 Vertel AB (<http://vertel.se>).
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


class Partner(models.Model):
    _inherit = "res.partner"

    # TODO: Copy these fields as well. Fix the calculate_age constrain.
    # A constrain should only throw a valueError, not perform a compute.
    # age = fields.Char(string="Age", compute="calculate_age")
    # jobseeker_category_id = fields.Many2one(comodel_name="res.partner.skat")
    # jobseeker_category = fields.Char(
    #    string="Jobseeker category", compute="combine_category_name_code")
    work_phone = fields.Char(string="Work phone", help="Work phone number")
    cfar = fields.Char(string="CFAR", help="CFAR number")
    customer_id = fields.Char(
        string="Customer number", help="Customer number", index=True)
    type = fields.Selection(
        selection_add=[
            ("foreign address", "Foreign Address"),
            ("given address", "Given address"),
            ("visitation address", "Visitation Address"),
            ("mailing address", "Mailing Address"),
        ])
    is_jobseeker = fields.Boolean(string="Jobseeker", index=True)
    is_independent_partner = fields.Boolean(string="Independent partner")
    is_government = fields.Boolean(string="Government")
    is_employer = fields.Boolean(string="Employer", index=True)
    customer_since = fields.Datetime(string="Customer since")
    jobseeker_work = fields.Boolean(string="Work")
    deactualization_date = fields.Datetime(string="Deactualization date")
    deactualization_reason = fields.Char(
        string="Deactualization reason"
    )
    foreign_country_of_work = fields.Char(string="When working in foreign country")
    registered_through = fields.Selection(
        selection=[
            ("pdm", "PDM"),
            ("self service", "Self service"),
            ("local office", "Local office"),
        ],
        string="Registered Through")
    share_info_with_employers = fields.Boolean(
        string="Share name and address with employers")
    sms_reminders = fields.Boolean(string="SMS reminders")
    visitation_address_id = fields.Many2one("res.partner", string="Visitation address")
    given_address_id = fields.Many2one("res.partner", string="given address")
    given_address_street = fields.Char(
        string="given address", related="given_address_id.street")
    segment_jobseeker = fields.Selection(
        string="Jobseeker segment",
        selection=[("a", "A"), ("b", "B"), ("c1", "C1"), ("c2", "C2"), ("c3", "C3")], )
    segment_employer = fields.Selection(
        string="Employer segment",
        selection=[
            ("including 1", "Including 1"),
            ("including 2", "Including 2"),
            ("entry job", "Entry job"),
            ("national agreement", "National agreement"),
            ("employment subsidy", "Employment subsidy"),
        ])
