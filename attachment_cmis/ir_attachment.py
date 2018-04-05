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
from openerp.exceptions import Warning
from cStringIO import StringIO
try:
    import cmislib
except:
    raise ImportError(_(u'Dependency failure: attachment_cmis requires python library "cmislib".'))
from cmislib import CmisClient

import logging
_logger = logging.getLogger(__name__)

# Documentation: https://chemistry.apache.org/python/docs/examples.html


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
                # acl = repo.getObject(xxx).getACL()
                # acl.entries.values()[0].permission
                self.datas = repo.getObject(self.store_fname).getContentStream().read().encode('base64')
            except Exception as e:
                self.datas = None
                _logger.warn('CMIS get datas except: %s' %e)

    @api.one
    def _cmis_set(self):
        file_size = len(self.datas.decode('base64'))
        repo = self.get_repo()
        if ((self.store_fname) and ('workspace' not in self.store_fname)) or not self.store_fname:
            parent = self.env['document.directory'].model2dir(self)
            try:
                doc = repo.createDocument(self.name.replace('/', '_'), 
                    parentFolder=self.env['document.directory'].model2dir(self).id, 
                    contentFile=StringIO(self.datas.decode('base64')))
                
            except Exception as e:
                _logger.warn('CMIS set create document except: %s' %e)
                return None
            try:
                self.store_fname = doc.getProperties().get('cmis:versionSeriesId')
            except Exception as e:
                _logger.warn('CMIS set get document properties except: %s' %e)
                return None
        else:
            # checkout and checkin
            try:
                doc = repo.getObject(self.store_fname).checkout()
                doc.setContentStream(contentFile=StringIO(self.datas.decode('base64')))
                doc.checkin(checkinComment='Checked In by Odoo: %s' %self.env.user.login)
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
        icp = self.env['ir.config_parameter']
        values = icp.get_param('attachment_cmis.remote_server')
        client_path = values.split(',')[0]
        admin_login = values.split(',')[1]
        admin_password = values.split(',')[2]
        try:
            client = CmisClient('http://192.168.1.124:8080/alfresco/cmisatom', 'admin@vertel.se', 'admin')
        except Exception as e:
            _logger.warn('get repo: %s' %e)
        return client.defaultRepository

    def cron_sync(self):
        repo = self.get_repo()
        # get latest token from a system paramet?
        #~ token = repo.info['latestChangeLogToken']
        #~ changes = repo.getContentChanges(changeLogToken='0')
        #~ for c in changes:
            #~ if c.changeType == 'created':
                #~ repo.getObject(c.objectId)


class document_directory(models.Model):
    _inherit = 'document.directory'

    remote_id = fields.Char(string='Remote ID')

    @api.one
    def check_remote_id(self,folder):
        if not self.remote_id:
            repo = self.env['ir.attachment'].get_repo()
            parent = repo.getRootFolder()
            folder_obj = None
            for f in folder.split('/'):
                if f != '':
                    try:
                        if parent.getPaths()[0] == '/':
                            folder_obj = repo.getObjectByPath('/%s' %(f))
                        else:
                            folder_obj = repo.getObjectByPath('/'.join(parent.getPaths()[0].split('/')+[f]))
                    except Exception as e:
                        # acl = folder_obj.getACL()
                        # acl.addEntry('GROUP_EVERYONE', 'cmis:write', 'true')
                        # folder_obj.applyACL(acl)
                        # folder_obj.getACL().getEntries().get('GROUP_EVERYONE').permissions
                        _logger.warn('GetObjectByPath: %s' % e)
                        folder_obj = None
                        try:
                            folder_obj = parent.createFolder(f, properties={})
                        except Exception as e:
                            _logger.warn('Create Folder: %s' %e)
                    parent = folder_obj
                _logger.warn('folder %s %s' % (f,folder_obj))
            _logger.warn('folder II %s' % (folder_obj))
            
            self.remote_id = folder_obj.id


    @api.model
    def model2dir(self, attachment):
        def _check_dir(dirname,parent_id,user_id,folder):
            directory = self.env['document.directory'].search([('name', '=', dirname), ('parent_id', '=', parent_id)],limit=1)
            if not directory:
                directory = self.env['document.directory'].create({
                    'name': dirname,
                    'user_id': user_id,
                    'parent_id': parent_id,
                })
            directory.check_remote_id(folder)
            _logger.warn('_check_dir %s %s' % (directory.name,directory.remote_id))
            return directory
        odoo_directory = _check_dir('odoo_models',False,self.env.ref('base.user_root').id,'/odoo_models')
        models_directory = _check_dir(attachment.res_model,odoo_directory.id,self.env.ref('base.user_root').id,'/odoo_models/%s' % attachment.res_model)
        object_directory = _check_dir('%s_%s' % (attachment.res_model,attachment.res_id),models_directory.id,self.env.ref('base.user_root').id,'/odoo_models/%s/%s' %(attachment.res_model,'%s_%s' % (attachment.res_model,attachment.res_id)))
        return self.env['ir.attachment'].get_repo().getObject(object_directory.remote_id)
        

