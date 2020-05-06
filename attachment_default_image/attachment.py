# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution, third party addon
#    Copyright (C) 2020 Vertel AB (<http://vertel.se>).
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
from openerp.modules import get_module_path
import os

import logging
_logger = logging.getLogger(__name__)

class ir_attachment(models.Model):
    _inherit='ir.attachment'

    @api.cr_uid
    def _file_read(self, cr, uid, fname, bin_size=False):
        full_path = self._full_path(cr, uid, fname)
        r = ''
        try:
            if bin_size:
                r = os.path.getsize(full_path)
            else:
                r = open(full_path,'rb').read().encode('base64')
        except:
            try:
                env = api.Environment(cr, uid, {})
                create_image = int(env['ir.config_parameter'].get_param('attachment_default_image.create_image', '0'))
                path = '%s/placeholder.png' % get_module_path('attachment_default_image')
                _logger.warn('\npath: %s\n', path)
                if create_image:
                    r = open(path, 'rb').read()
                    dir_path = '/'.join(full_path.split('/')[:-1])
                    if not os.path.isdir(dir_path):
                        os.mkdir(dir_path)
                    r_new = open(full_path,'wb')
                    r_new.write(r)
                    r_new.close()
                if bin_size:
                    r = os.path.getsize(path)
                else:
                    r = (r or open(path, 'rb').read()).encode('base64')
            except:
                _logger.exception("_read_file reading %s. Placeholder image also failed (%s).", full_path, path)
            _logger.exception("Using placeholder image (_read_file reading %s)", full_path)
        return r
