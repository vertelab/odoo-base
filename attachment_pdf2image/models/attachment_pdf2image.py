# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Enterprise Management Solution, third party addon
#    Copyright (C) 2017 Vertel AB (<http://vertel.se>).
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
from wand.image import Image
from wand.display import display
from wand.color import Color
import logging
_logger = logging.getLogger(__name__)

class ir_attachment(models.Model):
    _inherit='ir.attachment'

    @api.model
    def create(self, values):
        att = super(ir_attachment, self).create(values)
        #~ if self._context.get('convert') == 'pdf2image' and att.mimetype == 'application/pdf':
        if att.file_type == 'application/pdf':
            att.pdf2image(800,1200)
        return att

    @api.multi
    def pdf2image(self,dest_width, dest_height):
        RESOLUTION = 300
        for attachment in self:
            img = Image(blob=attachment.datas.decode('base64'),resolution=(RESOLUTION,RESOLUTION))
            img.background_color = Color('white')
            #img.resize(dest_width,dest_height)
            attachment.image = img.make_blob(format='jpg').encode('base64')
