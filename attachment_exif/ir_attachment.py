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

from openerp.modules import get_module_resource, get_module_path

try:
    import piexif
except:
    raise ImportError(_(u'Dependency failure: attachment_exif requires python library "piexif".'))


import logging
_logger = logging.getLogger(__name__)

# Document: https://pypi.python.org/pypi/piexif

class ir_attachment(models.Model):
    _inherit='ir.attachment'

    exif_ids = fields.One2many(comodel_name='ir.attachment.exif', inverse_name='attachment_id', string='Exif Data')

    @api.one
    def load_exif(self):
        if self.type == 'url':
            module = self.url.split('/')[1]
            path = '/'.join(self.url.split('/')[2:])
            #~ raise Warning(get_module_path(module),get_module_resource(module,path),module,path)
            exif_dict = piexif.load(get_module_resource(module,path))
        else:
            exif_dict = piexif.load(self.datas.decode('base64'))
        for ifd in ['0th','Exif','thumbnail','1th','GPS','Interop']:
            if exif_dict.get(ifd):
                for tag in exif_dict[ifd]:
                    label = self.env['ir.attachment.exif.label'].search([('name','=',piexif.TAGS[ifd][tag]["name"])])
                    if not label:
                        label = self.env['ir.attachment.exif.label'].create({'ifd': ifd,'name': piexif.TAGS[ifd][tag]['name'], 'exif_type': piexif.TAGS[ifd][tag]['type']} )
                    if not label.type == 'drop':
                        exif = self.env['ir.attachment.exif'].search([('attachment_id','=',self.id),('exif_label','=',label.id)])
                        if not exif:
                            try:
                                self.env['ir.attachment.exif'].create({
                                    'attachment_id': self.id,
                                    'exif_label': label.id,
                                    'exif_value': '%s' % (exif_dict[ifd][tag]),
                                })
                            except:
                                pass

    # TODO: write exif data when create or write
    #~ @api.model
    #~ def create(self):

    @api.multi
    def write(self, vals):
        if self.mimetype in ['image/jpeg','image/tiff']:
            self.load_exif()
        return super(ir_attachment, self).write(vals)
        
class ir_attachment_exif(models.Model):
    _name = 'ir.attachment.exif'

    attachment_id = fields.Many2one(comodel_name='ir.attachment')
    exif_label = fields.Many2one(comodel_name='ir.attachment.exif.label', string='Label')
    exif_value = fields.Text(string='Value')
    ifd = fields.Selection([],related='exif_label.ifd')
    type = fields.Selection([],related='exif_label.type')

class ir_attachment_exif_label(models.Model):
    _name = 'ir.attachment.exif.label'

    ifd = fields.Selection([('0th','Primary Image'),('1th','Thumbnail Image'),('Exif','Exif'),('thumbnail','Thumbnail'),('GPS','GPS'),('Interop','Interop')],string="IFD")
    name = fields.Char(string='name')
    type = fields.Selection([('drop','Drop'),('hide','Hide'),('view','View')],string="Type",default='view')
