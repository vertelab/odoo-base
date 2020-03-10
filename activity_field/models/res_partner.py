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
    
    activity = fields.Char(string="Activity", help="tab")
    latest_activity_date = fields.Datetime(string="Latest Activity Date", help="Date")
    latest_activity = fields.Char(string="Latest Activity", help="Latest Activity Text")
    next_activity_date = fields.Datetime(string="Next Activity Date", help="Date")
    next_activity = fields.Char(string="Next Activity", help="Next Activity Text")