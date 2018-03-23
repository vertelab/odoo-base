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

    datas = fields.Binary(compute='_cmis_get', inverse='_cmis_set', string='File Content', nodrop=True)

    @api.one
    def _cmis_get(self):
        if self.store_fname and 'workspace' not in self.store_fname:
            try:
                self.datas = open(self._full_path(self.store_fname),'rb').read().encode('base64')
            except IOError:
                self.datas = None
                _logger.error("CMIS get fileread: %s", self._full_path(self.store_fname))
        else:
            try:
                repo = self.get_repo()
                self.datas = repo.getObject(self.store_fname).getContentStream().read().encode('base64')
            except Exception as e:
                self.datas = None
                _logger.warn('CMIS get datas except: %s' %e)

    @api.one
    def _cmis_set(self):
        file_size = len(self.datas.decode('base64'))
        repo = self.get_repo()
        if ((self.store_fname) and ('workspace' not in self.store_fname)) or not self.store_fname:
            try:
            #~ doc = repo.createDocument(attach.name, properties={}, parentFolder=attach.parent_id.name, contentFile=StringIO(value), contentType=None, contentEncoding=None)
                self.store_fname = repo.createDocument(self.name.replace('/', '_'), parentFolder=self.get_directory(self.res_model), contentFile=StringIO(self.datas.decode('base64'))).id
            except Exception as e:
                _logger.warn('CMIS set create document except: %s' %e)
        else:
            # checkout and checkin
            try:
                doc = repo.getObject(self.store_fname).checkout()
                doc.setContentStream(contentFile=StringIO(self.datas.decode('base64')))
                doc.checkin(checkinComment='Checked In by Odoo')
            except Exception as e:
                _logger.warn('CMIS set checkin/out except: %s' %e)

    #~ @api.model
    #~ def create(self, values):
        #~ if (not values.get('parent_id', False)) and (values.get('res_model', False)):
            #~ values['parent_id'] = self.get_directory(values['res_model']).id
        #~ att = super(ir_attachment, self).create(values)
        #~ return att

    #~ @api.multi
    #~ def write(self, vals):
        #~ if (not vals.get('parent_id', False)) and (vals['res_model']):
            #~ vals['parent_id'] = self.get_directory(vals['res_model']).id
        #~ return super(ir_attachment, self).write(vals)

    @api.model
    def get_repo(self):
        try:
            client = CmisClient(CLIENT_PATH, LOGIN, PASSWORD)
        except Exception as e:
            _logger.warn('get repo: %s' %e)
        return client.defaultRepository

    @api.model
    def get_folder(self, path):
        repo = self.get_repo()
        def _get_folder(parent, folder):
            try:
                if parent.getPaths()[0] == '/':
                    folder_obj = repo.getObjectByPath('/%s' %(folder))
                else:
                    folder_obj = repo.getObjectByPath('/%s/%s' %('/'.join(parent.getPaths()[0].split('/')[1:]), folder))
            except:
                folder_obj = parent.createFolder(folder, properties={})
            return folder_obj
        parent = repo.getRootFolder()
        folder_obj = None
        for folder in path.split('/'):
            if folder != '':
                folder_obj = _get_folder(parent, folder)
                parent = folder_obj
        return folder_obj

    @api.model
    def get_directory(self, res_model):
        models_directory = self.env['document.directory'].search([('name', '=', 'odoo_models'), ('parent_id', '=', False)])
        if not models_directory:
            models_directory = self.env['document.directory'].create({
                'name': 'odoo_models',
                'user_id': self.env.ref('base.user_root').id,
            })
        directory = self.env['document.directory'].search([('name', '=', res_model or 'other'), ('parent_id', '=', models_directory.id)])
        if not directory:
            directory = self.env['document.directory'].create({
                'name': res_model or 'other',
                'user_id': self.env.ref('base.user_root').id,
                'parent_id': models_directory.id,
            })
        folder = self.get_folder('/odoo_models/%s' %directory.name)
        if directory.remote_id == '':
            directory.remote_id = folder.id
        return folder


class document_directory(models.Model):
    _inherit = 'document.directory'

    remote_id = fields.Char(string='Remote ID')
