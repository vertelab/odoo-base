# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution, third party addon
#    Copyright (C) 2018- Vertel AB (<http://vertel.se>).
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
from cStringIO import StringIO
try:
    import cmislib
except:
    raise ImportError(_(u'Dependency failure: attachment_cmis requires python library "cmislib".'))
from cmislib import CmisClient

import logging
_logger = logging.getLogger(__name__)

# Documentation: https://chemistry.apache.org/python/docs/examples.html

CLIENT_PATH = 'http://192.168.1.124:8080/alfresco/cmisatom'
LOGIN = 'admin'
PASSWORD = 'admin'


class ir_attachment(models.Model):
    _inherit='ir.attachment'

    @api.multi
    def _data_get(self, name, arg):
        result = {}
        bin_size = self._context.get('bin_size')
        for attach in self:
            result[attach.id] = self._file_read_cmis(attach.store_fname, bin_size)
        return result

    @api.model
    def _file_read_cmis(self, fname, bin_size=False):
        client = CmisClient(CLIENT_PATH, LOGIN, PASSWORD)
        repo = client.defaultRepository
        test_file = repo.getObject(fname)
        r = ''
        try:
            r = test_file.getContentStream().read().encode('base64')
        except IOError:
            _logger.exception("_read_file reading %s", fname)
        if bin_size:
            r = test_file.getProperties().get('cmis:contentStreamLength')
        return r

    @api.model
    def _data_set(self, id, name, value, arg):
        # We dont handle setting data to null
        if not value:
            return True
        file_size = len(value.decode('base64'))
        attach = self.env['ir.attachment'].browse(id)
        client = CmisClient(CLIENT_PATH, LOGIN, PASSWORD)
        repo = client.defaultRepository
        if not attach.store_fname:
            #~ doc = repo.createDocument(attach.name, properties={}, parentFolder=attach.parent_id.name, contentFile=StringIO(value), contentType=None, contentEncoding=None)
            doc = repo.createDocument(attach.name, contentFile=StringIO(value))
            attach.store_fname = doc.id
        else:
            # write properties and file name
            doc = repo.getObject(attach.store_fname)
        return True

    def _file_write_cmis(self, cr, uid, value):
        bin_value = value.decode('base64')
        fname, full_path = self._get_path(cr, uid, bin_value)
        if not os.path.exists(full_path):
            try:
                with open(full_path, 'wb') as fp:
                    fp.write(bin_value)
            except IOError:
                _logger.exception("_file_write writing %s", full_path)
        return fname
