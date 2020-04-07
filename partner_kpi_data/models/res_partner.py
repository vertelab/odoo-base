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
    
    kpi_ids = fields.One2many(comodel_name="res.partner.kpi", inverse_name="partner_id")

   


class ResPartnerKpi(models.Model):
    _name="res.partner.kpi"
    
    partner_id = fields.Many2one(comodel_name="res.partner")
    #name = fields.Char(string="", help="", required=True)
    fiscal_year = fields.Datetime(string="Fiscal year")
    turnover = fields.Integer(string="Turnover")
    turnover_change = fields.Integer(string="Change")
    turnover_change_percent = fields.Integer(string="Change %")
    profit = fields.Integer(string="Profit")
    profit_percent = fields.Integer(string="Profit %") #profit/turnover
    profit_change = fields.Integer(string="Change")
    profit_change_percent = fields.Integer(string="Change %")
    employees = fields.Integer(string="Employees")
    employee_change = fields.Integer(string="Change")
    employee_change_percent = fields.Integer(string="Change %")
    
    @api.one
    def compute_profit_percent(self):
        profit_decimal = (float(self.profit) / self.turnover)
        if profit_decimal > 1:
            profit_decimal = profit_decimal -1
        else:
            profit_decimal = 1 - profit_decimal

        profit_decimal = profit_decimal * 100
        profit_decimal = round(profit_decimal, 0)
        self.profit_percent = int(profit_decimal)

            
        
    
