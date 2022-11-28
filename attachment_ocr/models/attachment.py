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
from odoo import models, fields, api, _
import subprocess
import pytesseract
import pdfplumber
from base64 import b64decode
import tempfile
from PIL import Image
import PyPDF2

import logging

_logger = logging.getLogger(__name__)


class IRAttachment(models.Model):
    _inherit = 'ir.attachment'

    def ocr2index(self):
        active_ids = self.env.context.get('active_ids')
        attachment_ids = self.env['ir.attachment'].browse(active_ids)

        for attachment in attachment_ids:
            all_text = ''
            with tempfile.NamedTemporaryFile('w+b', suffix='.pdf') as tmpfile:
                bytes = b64decode(attachment.datas, validate=True)
                tmpfile.write(bytes)
                tmpfile.seek(0)
                with pdfplumber.open(tmpfile.name) as pdf:
                    for page in pdf.pages:
                        page_content = page.extract_text(layout=True)
                        all_text = all_text + '\n' + page_content
            attachment.index_content = all_text

        # Former Code --
        # stdout, stderr = process.communicate(attachment.image.decode('base64'))
        # if process.returncode:
        #     _logger.error('Error during OCR: %s', stderr)
        # if stdout:
        #     attachment.index_content += u'%s' % stdout.decode('utf-8')
