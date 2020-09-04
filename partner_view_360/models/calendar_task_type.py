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
_logger = logging.getLogger(__name__)


class CalendarTaskType(models.Model):
    _inherit = "calendar.task.type" 

    code = fields.Char(string='Code', size=8, trim=True, )
    name = fields.Char(string='Name', size=25, trim=True, )
    right_type = fields.Selection(string='Right Type', selection=[('','N/A'),('STARK','Stark'),('MYCKET_STARK','Mycket Stark')] )
    reason_code = fields.Char(string='Reason Code', size=3, trim=True, )
    reason = fields.Char(string='Reason', size=25, trim=True, )
    interval = fields.Selection(selection=[('1','1 day'),('7','1 week'),('14','2 weeks'),('30','30 days'),('60','60 days'),('100','100 days'),('365','a Year')],string='Interval',default='1')
    client_responsible = fields.Boolean(string='Client Responsible', help="Change current user to be responsible for this client, and get permanent rights that goes with it")
    
    @api.one
    def default_name(self):
        self.display_name = "[%s] %s" % (self.code, self.name)
        
