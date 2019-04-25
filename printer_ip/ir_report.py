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
from openerp.http import request


class IrActionsReportXml(models.Model):
    _inherit = 'ir.actions.report.xml'
    
    ip_ids = fields.One2many(comodel_name='ir.ip.report.action',inverse_name='report_id',
                              string='IP',
        help='This field allows configuring action and printer on a per '
             'ip/host basis'
    )
                        
class ir_ip_report_action(models.Model):
    """
    Ip and actions
    """
    _name = 'ir.ip.report.action'
    _description = 'Report Printing Actions for IP'

    def _available_action_types(self):
        return [('server', 'Send to Printer'),
                ('client', 'Send to Client'),
                ('user_default', "Use user's defaults"),
                ]
    
    report_id = fields.Many2one(comodel_name='ir.actions.report.xml',
                                string='Report',
                                required=True,
                                ondelete='cascade')
    name = fields.Char(string='IP or host',
                       required=True,
                       ondelete='cascade')
    printing_action = fields.Selection(_available_action_types,
                                       required=True)
    printing_printer_id = fields.Many2one(comodel_name='printing.printer',
                                          string='Printer')
                                          
    @api.multi
    def behaviour(self):
        if not self:
            return {}
        return {'action': self.printing_action,
                'printer': self.printing_printer_id,
                }
                                          
class ReportXMLAction(models.Model):
    _inherit = 'ir.actions.report.xml'

    def get_client_ip(self):
        return(request.httprequest.environ['REMOTE_ADDR'])


    @api.multi
    def behaviour(self):
        self.ensure_one()
        res = super(ReportXMLAction, self).behaviour()
        
        for report in self:
            printing_act_obj = self.env['ir.ip.report.action'].browse( [ ('report_id', '=', report.id) ] )
            
            if printing_act_obj:
                report['action'] = printing_act_obj.printing_action
                report['printer'] = printing_act_obj.printing_printer_id
            
            res[report.id] = report
        
        return res

        
