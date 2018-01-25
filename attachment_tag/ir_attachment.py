# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution, third party addon
#    Copyright (C) 2004-2016 Vertel AB (<http://vertel.se>).
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


class ir_attachment_tag(models.Model):
    _name = 'ir.attachment.tag'

    name = fields.Char(string='Name', required=True, translate=True)


class ir_attahment(models.Model):
    _inherit = 'ir.attachment'

    tag_ids = fields.Many2many(comodel_name='ir.attachment.tag', string='Tags')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
