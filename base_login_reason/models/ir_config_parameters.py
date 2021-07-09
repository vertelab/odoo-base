# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution, third party addon
#    Copyright (C) 2004-2021 Vertel AB (<http://vertel.se>).
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

from odoo import api, models, tools

DELAY_KEY = 'inactive_session_time_out_delay'
IGNORED_PATH_KEY = 'inactive_session_time_out_ignored_url'


class IrConfigParameter(models.Model):
    _inherit = 'ir.config_parameter'

    @api.model
    @tools.ormcache('self.env.cr.dbname')
    def _auth_timeout_get_parameter_delay(self):
        return int(
            self.env['ir.config_parameter'].sudo().get_param(
                DELAY_KEY, 7200,
            )
        )

    @api.model
    @tools.ormcache('self.env.cr.dbname')
    def _auth_timeout_get_parameter_ignored_urls(self):
        urls = self.env['ir.config_parameter'].sudo().get_param(
            IGNORED_PATH_KEY, '',
        )
        return urls.split(',')

    @api.multi
    def write(self, vals):
        res = super(IrConfigParameter, self).write(vals)
        self._auth_timeout_get_parameter_delay.clear_cache(
            self.filtered(lambda r: r.key == DELAY_KEY),
        )
        self._auth_timeout_get_parameter_ignored_urls.clear_cache(
            self.filtered(lambda r: r.key == IGNORED_PATH_KEY),
        )
        return res
