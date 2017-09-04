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
import base64
import os

import logging
_logger = logging.getLogger(__name__)

# Document: https://pypi.python.org/pypi/piexif

class ir_attachment(models.Model):
    _inherit='ir.attachment'

    @api.model
    def load_document(self,document):
        _logger.warn('File to upload %s' % document)
        base = document.split('/')
        (basename,ext) = base[-1].split('.')
        _logger.warn('Basename %s extention %s' % (basename,ext))
        model = None
        res_id = None
        if self.load_document_object(basename):
            model = self.load_document_object(basename)._name
            res_id = self.load_document_object(basename).id
            _logger.warn('model %s res_id %s' % (self.load_document_object(basename)._name,self.load_document_object(basename).id))
        
        blob = open(document,'r')
        attachment = self.env['ir.attachment'].create({
                'name': '%s.%s' % (basename,ext),
                'res_name': basename,
                'res_model': model,
                'res_id': res_id,
                'datas': base64.encodestring(blob.read()),
                'datas_fname': basename,
            })
        blob.close()
        if attachment.mimetype in ['image/jpeg','image/png','image/gif']:
            attachment.load_exif()
            
        os.remove(document)
        
        return True
        
    def load_document_object(self,basename):
        if self.env['res.partner'].search([('name','=',basename)]):
            return self.env['res.partner'].search([('name','=',basename)])
        if self.env['res.users'].search([('name','=',basename)]):
            return self.env['res.users'].search([('name','=',basename)])
        return None

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
