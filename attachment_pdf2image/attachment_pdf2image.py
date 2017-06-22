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
        if self._context.get('convert') == 'pdf2image' and att.mimetype == 'application/pdf':
        #~ if att.mimetype == 'application/pdf':
            att.pdf2image(800,1200)
        return att

    @api.multi
    def pdf2image(self,dest_width, dest_height):
        RESOLUTION = 300
        #~ blob = self.datas.decode('base64')
        #~ raise Warning(self.base64_decode(self.datas))
        #~ str = self.datas + '=' *(-len(self.datas)%4)
        #~ img = Image(blob=self[0].datas.decode('base64'))
        #~ img.resize(dest_width,dest_height)
        #~ self[0].image = img.make_blob(format='jpg').encode('base64')
        img = Image(blob=self[0].datas.decode('base64'),resolution=(RESOLUTION,RESOLUTION))
        img.background_color = Color('white')
        self[0].image = img.make_blob(format='jpg').encode('base64')
        #~ return
        #~ try:
            #~ with Image(blob=self[0].datas.decode('base64'), resolution=(RESOLUTION,RESOLUTION)) as img:
                #~ img.background_color = Color('white')
                #~ img_width = img.width
                #~ ratio = dest_width / img_width
                #~ img.resize(dest_width, dest_height)
                #~ img.format = 'jpeg'
                #~ self[0].image = img.make_blob(format='jpeg').encode('base64')
        #~ except Exception as e:
            #~ return None
            #~ return None
