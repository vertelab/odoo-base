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
    turnover_change = fields.Integer(compute="compute_turnover_change")
    turnover_change_percent = fields.Integer(string="Change %")
    profit = fields.Integer(string="Profit")
    profit_percent = fields.Integer(compute="compute_profit_percent") #profit/turnover
    profit_change = fields.Integer(string="Change")
    profit_change_percent = fields.Integer(string="Change %")
    employees = fields.Integer(string="Employees")
    employee_change = fields.Integer(string="Change")
    employee_change_percent = fields.Integer(string="Change %")
    size = fields.Selection(selection=[
    ('1', 'Class 1'), 
    ('2', 'Class 2'), 
    ('3', 'Class 3'), 
    ('4', 'Class 4'), 
    ('5', 'Class 5'),
    ('6', 'Class 6'),
    ('7', 'Class 7'),
    ('8', 'Class 8'),
    ('9', 'Class 9')], 
    string='Size class', 
    default='1', 
    help="Size class")
    
    @api.one
    def compute_profit_percent(self):
        decimal = (float(self.profit) / self.turnover)
        if decimal > 1:
            decimal = decimal -1
        else:
            decimal = 1 - decimal
            decimal = decimal * -1

        decimal = decimal * 100
        decimal = round(decimal, 0)
        self.profit_percent = int(decimal)
    
    @api.one
    def compute_turnover_change(self):
        previous = self.env['res.partner.kpi'].search([('turnover', '<', self.turnover)], order='fiscal_year DESC', limit=1)
        self.turnover_change = self.turnover - previous.turnover
    @api.one
    def compute_profit_change(self):
        previous = self.env['res.partner.kpi'].search([('profit', '<', self.profit)], order='fiscal_year DESC', limit=1)
        self.profit_change = self.profit - previous.profit
    @api.one
    def compute_employees_change(self):
        previous = self.env['res.partner.kpi'].search([('employees', '<', self.employees)], order='fiscal_year DESC', limit=1)
        self.employees_change = self.employees - previous.employees
    
    @api.one
    def compute_turnover_change_percent(self):
        decimal = (float(self.turnover_change) / self.turnover)
        decimal = decimal * 100
        decimal = round(decimal, 0)
        self.turnover_change_percent = int(decimal)
    
    @api.one
    def compute_profit_change_percent(self):
        decimal = (float(self.profit_change) / self.profit)
        decimal = decimal * 100
        decimal = round(decimal, 0)
        self.profit_change_percent = int(decimal)
    
    @api.one
    def compute_employees_change_percent(self):
        decimal = (float(self.profit) / self.turnover)
        decimal = decimal * 100
        decimal = round(decimal, 0)
        self.employees_change_percent = int(decimal)
    

            
        
    
