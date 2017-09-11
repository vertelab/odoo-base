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
import subprocess
from StringIO import StringIO

import logging
_logger = logging.getLogger(__name__)

class ir_attachment(models.Model):
    _inherit='ir.attachment'

   
    #~ @api.model
    #~ def create(self, values):
        #~ att = super(ir_attachment, self).create(values)
        #~ if att.mimetype == 'application/pdf':
            #~ att.pdf2image(800,1200)
        #~ return att

    @api.multi
    def ocr2index(self):
        for attachment in self:
            process = subprocess.Popen(
                ['tesseract', '-l','swe+eng','stdin', 'stdout'],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            stdout, stderr = process.communicate(attachment.image.decode('base64'))
            if process.returncode:
                _logger.error('Error during OCR: %s', stderr)
            if stdout:
                attachment.index_content += u'%s' % stdout.decode('utf-8')
