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
        if att.mimetype in ['image/jpeg','image/png','image/gif']:
            att.image_orientation()
        return att

    @api.multi
    def image_orientation(self):
        RESOLUTION = 300
        orientation = {
            'top_left': 0,
            'left_top': 0,
            'right_top': 90,
            'top_right': 90,
            'right_bottom': 180,
            'bottom_right': 180,
            'left_bottom': 270,
            'bottom_left': 270,
        }
        try:
            img = Image(blob=self[0].datas.decode('base64'),resolution=(RESOLUTION,RESOLUTION))
            img.rotate(orientation.get(img.orientation))
            self[0].datas = base64.encodestring(img.make_blob(format='jpg'))
        except:
            pass
