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
    
    partner_activity_ids = fields.One2many(comodel_name="res.partner.activity", inverse_name="partner_id")
    

    @api.one
    def compute_activities_count(self):
            for partner in self:
                partner.activities_count = len(partner.activity_ids)
    activities_count = fields.Integer(compute='compute_activities_count')

    @api.multi
    def open_partner_activities(self):
        return{
            'name': _('Activities'),
            'domain':[('partner_id', '=', self.ids)],
            'view_type': 'form',
            'res_model': 'res.partner.activity',
            'view_id':  False,
            'view_mode': 'tree,kanban,form', #calendar: insufficient fields for calendar view
            'type': 'ir.actions.act_window',
        }

#TODO: Change name
class ResPartnerActivity(models.Model):
    _name="res.partner.activity"
    
    partner_id = fields.Many2one(comodel_name="res.partner")
    name = fields.Char(string="Activity Description", help="")
    meeting_type = fields.Many2one(comodel_name="res.partner.activity.type") #gör till lista, gör att auto_digital_dialogue tar inskrivningsdatum från en meeting type = "inskrivning"
    meeting_type_parent = fields.Many2one(comodel_name='res.partner.activity.type', related="meeting_type.parent_id")
    start_date = fields.Datetime(string="Start date", help="", required=True)
    done_before_date = fields.Datetime(string="Done before date")
    duration = fields.Float(string="Duration", help="")
    notes = fields.Char(string="Notes", help="")
    office_id = fields.Many2one('hr.department', related="partner_id.office", string="Location")
    mandatory = fields.Boolean(string="Mandatory")
    done = fields.Boolean(string="Done")

class ResPartnerActivityType(models.Model):
    _name="res.partner.activity.type"

    activity_id = fields.One2many(comodel_name="res.partner.activity", inverse_name="meeting_type")
    name = fields.Char(string="Meeting type", help="")
    description = fields.Char(string="Description", help="")
    parent_id = fields.Many2one(comodel_name='res.partner.activity.type', string='Parent')
    #more fields?


