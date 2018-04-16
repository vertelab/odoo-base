# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution, third party addon
#    Copyright (C) 2018- Vertel AB (<http://vertel.se>).
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
from openerp import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)


class remote_server_configuration(models.TransientModel):
    _inherit = 'knowledge.config.settings'

    remote_server = fields.Selection(selection_add=[('cmis_alfresco.client_path,cmis_alfresco.admin_login,cmis_alfresco.admin_password', 'Alfresco')], string='Select Remote Server')
    client_path = fields.Char(string='Client Path')
    admin_login = fields.Char(string='Admin Login')
    admin_password = fields.Char(string='Admin Password')

    @api.model
    def get_default_alfresco_values(self, fields):
        return {
            'client_path': self.env['ir.config_parameter'].get_param('cmis_alfresco.client_path', ''),
            'admin_login': self.env['ir.config_parameter'].get_param('cmis_alfresco.admin_login', ''),
            'admin_password': self.env['ir.config_parameter'].get_param('cmis_alfresco.admin_password', ''),
        }

    @api.multi
    def set_alfresco_values(self):
        if not self.env['ir.config_parameter'].get_param('attachment_cmis.remote_server'):
            self.env['ir.config_parameter'].set_param(key='attachment_cmis.remote_server', value='cmis_alfresco.client_path,cmis_alfresco.admin_login,cmis_alfresco.admin_password')
        for record in self:
            self.env['ir.config_parameter'].set_param(key="cmis_alfresco.client_path", value=record.client_path)
            self.env['ir.config_parameter'].set_param(key="cmis_alfresco.admin_login", value=record.admin_login)
            self.env['ir.config_parameter'].set_param(key="cmis_alfresco.admin_password", value=record.admin_password)
