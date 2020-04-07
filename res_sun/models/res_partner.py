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
import logging
_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    sun_id = fields.Many2one(comodel_name='res.sun', string='SUN Code')
    
    education_level = fields.Many2one(comodel_name="res.partner.education_level", string="Education level")

    foreign_education = fields.Boolean(string="Foreign education")
    foreign_education_approved = fields.Boolean(string="Foreign education approved")

class ResPartnerEducationLevel(models.Model):
    _name="res.partner.education_level"

    partner_id = fields.One2many(comodel_name="res.partner", inverse_name="education_level")

    name = fields.Integer(string="Education level") #2
    description = fields.Char(string="Description") #förgymnasial utbildning 9 (10) år