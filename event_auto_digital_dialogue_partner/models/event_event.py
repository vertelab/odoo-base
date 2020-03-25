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

class EventEvent(models.Model):
    _inherit = "event.event" 
    

    registration_date = fields.Datetime(string="Registration date")
    recipients = fields.Many2many('res.partner', string="Recipients")

    @api.one
    def compute_recipients_count(self):
        self.recipients_count = len(self.recipients)

    recipients_count = fields.Integer(compute='compute_recipients_count')
    
#    for recipient in recipients:
#        for activity in recipient.activites_ids:
#            if activity.meeting_type.name == "registration":
#                registration_date = activity.start_date

    
    #registration_date = fields.Char(string="Registration date", help="Date that the job-seeker was entered into the system") #temporärt, ska tas från arbetssökande kundkortet


class ResPartner(models.Model):
    _inherit = "res.partner"

    events = fields.Many2many('event.event', string="Events")