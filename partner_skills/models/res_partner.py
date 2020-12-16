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

    skills = fields.Many2many('hr.skill', string="Skill")
    skill_id = fields.Char(string="Skill", related="skills.complete_name")

    other_experiences = fields.Many2many('hr.other.experiences', string="Other Experience")
    strengths = fields.Many2many('hr.strengths', string="Strengths")
    interests = fields.Many2many('hr.interests', string="Interests")
    partner_skill_ids = fields.One2many(
        string='Skills',
        comodel_name='hr.employee.skill',
        inverse_name='partner_id',
    )


class PartnerSkill(models.Model):
    _inherit = 'hr.employee.skill'

    partner_id = fields.Many2one(
        string='Partner',
        comodel_name='res.partner',
    )


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    skill = fields.Many2one(string="Skill", related="employee_skill_ids.skill_id")


class OtherExperiences(models.Model):
    _name = 'hr.other.experiences'
    description = "Experiences"

    name = fields.Char(string="Experience")


class Strengths(models.Model):
    _name = 'hr.strengths'
    description = "Strengths"

    name = fields.Char(string="Strengths")


class Interests(models.Model):
    _name = 'hr.interests'
    description = "Interests"

    name = fields.Char(string="Interests")
