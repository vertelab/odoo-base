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
    
   

    activities_ids = fields.One2many(comodel_name="res.partner.activity", inverse_name="partner_id")

class ResPartnerActivity(models.Model):
    _name="res.partner.activity"
    
    partner_id = fields.Many2one(comodel_name="res.partner")

    name = fields.Char(string="Subject", help="", required=True)
    meeting_type = fields.Char(string="Meeting type", help="Type of meeting")
    start_date = fields.Datetime(string="Start date", help="", required=True)
    duration = fields.Float(string="Duration", help="", required=True)
    notes = fields.Char(string="Notes", help="")
    location = fields.Char(string="Location", help="")

