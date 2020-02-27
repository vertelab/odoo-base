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

class IrModelFields(models.Model):
    _inherit = 'ir.model.fields'

    map_system = fields.Char(string='Mapped system', help="The name of the mapped system")
    map_table = fields.Char(string='Mapped system table', help="The name of the table in the mapped system")
    map_field = fields.Char(string='Mapped system field', help="The name of the field in the mapped system")
    map_odoo_master = fields.Boolean(string='Odoo master', help="Is Odoo master of the data?")
    map_type = fields.Char(string='Mapped type', help="The type of the mapped system field")
    map_comment = fields.Char(string='Comment', help="Comment regarding the mapping")
