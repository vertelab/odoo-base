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

    remote_server = fields.Selection([], string='Select Remote Server')

    @api.model
    def get_default_remote_server_values(self, fields):
        icp = self.env['ir.config_parameter']
        return {
            'remote_server': icp.get_param('attachment_cmis.remote_server'),
        }

    @api.multi
    def set_remote_server_values(self):
        icp = self.env['ir.config_parameter']
        for record in self:
            icp.set_param(key="attachment_cmis.remote_server", value=record.remote_server)
