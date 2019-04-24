# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Yannick Vaucher
#    Copyright 2013 Camptocamp SA
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
from openerp import models, fields, api



class IrActionsReportXml(models.Model):
    _inherit = 'ir.actions.report.xml'
        
    ip_ids = fields.One2many(comodel_name='ir.ip.report.action',inverse_name='',
                              string='IP',
        help='This field allows configuring action and printer on a per '
             'ip/host basis'
                              )
                        
class ir_ip_report_action(models.Model):
    """
    Ip and actions
    """
    _name = 'ir.ip.report.action'


    def _available_action_types(self):
        return [('server', 'Send to Printer'),
                ('client', 'Send to Client'),
                ]
    
    name = fields.Char(string='IP or host')
    printing_action = fields.Selection(_available_action_types)
    printing_printer_id = fields.Many2one(comodel_name='printing.printer',
                                          string='Default Printer')
     

class ReportXMLAction(models.Model):
    _inherit = 'printing.report.xml.action'

    @api.multi
    def behaviour(self):
        self.ensure_one()
        res = super(ReportXMLAction, self).behaviour()
        res['tray'] = self.printer_tray_id.system_name
        return res

        
