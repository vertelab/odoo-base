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
    _inherit = "res.partner" 
    
    job_ids = fields.One2many(comodel_name="res.partner.jobs", inverse_name="partner_id")


class Jobs(models.Model):
    _name = 'res.partner.jobs'

    partner_id = fields.Many2one(comodel_name="res.partner")
    
    name = fields.Many2one('res.ssyk', string="Job title") 
    ssyk_code = fields.Char(string="SSYK", related="name.code")
    education_level = fields.Many2one(comodel_name="res.partner.education_level", string="Education level")
    experience_length = fields.Selection([(0, 'No Experience'),
                                          (1, 'Less than 1 year'),
                                          (2, '1 to 3 years'),
                                          (3, 'More than 3 years')
                                          ])
    education = fields.Boolean(string="Education") 
    experience = fields.Boolean(string="Experience")

    @api.onchange('experience_length')
    def _tick_untick_experience(self):
        if self.experience_length != 0:
            self.experience = True
        else:
            self.experience = False

    @api.onchange('education_level')
    def _tick_untick_education(self):
        if self.education_level.name != 0:
            self.education = True
        else:
            self.education = False
