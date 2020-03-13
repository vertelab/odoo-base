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

class AccountAnalyticLine(models.Model):
   _inherit = "account.analytic.line" 
   #_name = ""
   # code = fields.Char(string="Code", help="Code") #borde sitta ihop med project_task
   
   # We use a many2one relation to our new model project.task.code. Each account.analytic.line can only have 1 code. 
   # project.task.code stores data about the code. 
   code_id = fields.Many2one(comodel_name="project.task.code", string="Code", help="Code") 