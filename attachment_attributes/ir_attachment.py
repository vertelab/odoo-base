# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution, third party addon
#    Copyright (C) 2004-2017 Vertel AB (<http://vertel.se>).
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
from wand.image import Image
from wand.display import display
from wand.color import Color
import logging
_logger = logging.getLogger(__name__)

class ir_attachment(models.Model):
    _inherit='ir.attachment'

    attribute_ids = fields.One2many(compel_name="ir.attachment.attributes")

class ir_attachment_attributes(models.Model):
    _name="ir.attachment.attributes"
   
    attachment_id = fields.Many2one(comodel_name="ir.attachment")
    value = fields.Text(string="Value")
    label = fields.Many2one(comodel_name='ir.attachment.attributes.label')
    
class ir_attachment_attributes_label(models.Model):
    _name="ir.attachment.attributes.label"
   
    name = fields.Char(string="Name")
