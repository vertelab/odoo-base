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

CMIS_CLIENT = False
CMIS_SERVER = False
CMIS_LOGIN = {}
try:
    import cmislib
except:
    raise ImportError(_(u'Dependency failure: attachment_cmis requires python library "cmislib".'))
from cmislib import CmisClient

import logging
_logger = logging.getLogger(__name__)

# Documentation: https://chemistry.apache.org/python/docs/examples.html


class cmis_repo(object):
    def __init__(self,fw):
        global CMIS_CLIENT,CMIS_LOGIN,CMIS_SERVER
        try:
            self.personal_repo = CMIS_LOGIN[self.env.cr.dbname][self.env.uid]['client'].defaultRepository
        except Exception as e:
            self.personal_repo = None
        try:
            self.repo = CMIS_CLIENT.defaultRepository
        except Exception as e:
            self.repo = None
        if not self.repo:
            values = fw.env['ir.config_parameter'].get_param('attachment_cmis.remote_server')
            CMIS_SERVER = values.split(',')[0]
            CMIS_CLIENT = CmisClient(CMIS_SERVER,values.split(',')[1],values.split(',')[2])
            self.repo = CMIS_CLIENT.defaltRepository
            
        _logger.warn('CMIS_repo : general %s personal %s'  %(self.repo,self.personal_repo))
    def getObject(self,remote_id):
        try:
            return self.personal_repo.getObject(remote_id)
        except Exception as e:
            _logger.warn('CMIS_repo personal client: %s' %e)
        try:
            return self.repo.getObject(remote_id)
        except Exception as e:
            _logger.warn('CMIS_repo general client: %s' %e)
        return None

    def createDocument(self,**kw):
        try:
            return self.personal_repo.createDocument(**kw)
        except Exception as e:
            _logger.warn('CMIS_repo personal client: %s' %e)
        try:
            return self.repo.createDocument(**kw)
        except Exception as e:
            _logger.warn('CMIS_repo general client: %s' %e)
        return None    
    
        #~ repo.createDocument(self.name.replace('/', '_'), 
                    #~ parentFolder=self.getFolder(), 
                    #~ contentFile=StringIO(self.datas.decode('base64')))
    def getRootFolder(self):
        try:
            return self.personal_repo.getRootFolder()
        except Exception as e:
            _logger.warn('CMIS_repo personal client: %s' %e)
        try:
            return self.repo.getRootFolder()
        except Exception as e:
            _logger.warn('CMIS_repo general client: %s' %e)
        return None

    def getObjectByPath(self,path):
        try:
            return self.personal_repo.getObjectByPath(path)
        except Exception as e:
            _logger.warn('CMIS_repo personal client: %s' %e)
        try:
            return self.repo.getObjectByPath(path)
        except Exception as e:
            _logger.warn('CMIS_repo general client: %s' %e)
        return None    


class ir_attachment(models.Model):
    _inherit='ir.attachment'

    datas = fields.Binary(compute='_cmis_get', inverse='_cmis_set', string='File Content', nodrop=True)
    remote_id = fields.Char(string='Remote ID')
    
    
    @api.one
    def _cmis_get(self):
        if self.type =='url':
            pass
        elif self.remote_id:  # CMIS
            try:
                repo = cmis_repo()
                # acl = repo.getObject(xxx).getACL()
                # acl.entries.values()[0].permission
                self.datas = repo.getObject(self.remote_id).getContentStream().read().encode('base64')
            except Exception as e:
                self.datas = None
                _logger.warn('CMIS get datas except: %s' %e)
        else: # not in CMIS, fallback
            try: 
                _logger.error('CMIS Fallback %s' % self.id)
                res = super(ir_attachment, self)._data_get(self.name,{}) # Fallback open(self._full_path(self.store_fname),'rb').read().encode('base64')
                self.datas = res[res.keys()[0]]
            except IOError:
                self.datas = None
                _logger.error("CMIS fallback error: %s", self._full_path(self.store_fname))

    @api.one
    def _cmis_set(self):
        if self.type == 'url':
            return super(ir_attachment, self)._data_set(self.name,self.datas)
        file_size = len(self.datas.decode('base64'))
        repo = cmis_repo()
        if not self.remote_id:
            try:
                doc = repo.createDocument(self.name.replace('/', '_'), 
                    parentFolder=self.getFolder(), 
                    contentFile=StringIO(self.datas.decode('base64')))
            except Exception as e: # Fallback
                _logger.warn('CMIS set create document except: %s' %e)
                super(ir_attachment, self)._data_set(self.name,self.datas)
                return None
            try:
                self.remote_id = doc.getProperties().get('cmis:versionSeriesId')
            except Exception as e:
                _logger.warn('CMIS set get document properties except: %s' %e)
                # raise Warning()
                return None
        else:
            # checkout and checkin
            try:
                doc = repo.getObject(self.remote_id).checkout()
                doc.setContentStream(contentFile=StringIO(self.datas.decode('base64')))
                doc.checkin(checkinComment='Checked In by Odoo: %s' %self.env.user.login)
            except Exception as e:
                _logger.warn('CMIS set checkin/out except: %s' %e)
                # No Fallback raise Warning()


    @api.multi
    def unlink(self):
        for a in self:
            if a.remote_id:
                cmis_repo().getObject(a.remote_id).delete()
        return super(ir_attachment, self).unlink()  

    @api.model
    def get_repo(self):
        global CMIS_CLIENT,CMIS_LOGIN,CMIS_SERVER
        if self.env.cr.dbname in CMIS_LOGIN.keys() and self.env.uid in CMIS_LOGIN[self.env.cr.dbname].keys() and CMIS_LOGIN[self.env.cr.dbname][self.env.uid]['client']:
            return CMIS_LOGIN[self.env.cr.dbname][self.env.uid]['client'].defaultRepository
        if CMIS_CLIENT:
            return CMIS_CLIENT.defaultRepository
        return None

        #~ icp = self.env['ir.config_parameter']
        #~ values = icp.get_param('attachment_cmis.remote_server')
        #~ client_path = values.split(',')[0]
        #~ admin_login = values.split(',')[1]
        #~ admin_password = values.split(',')[2]
        #~ try:
            #~ client = CmisClient('http://192.168.1.124:8080/alfresco/cmisatom', 'admin@vertel.se', 'admin')
        #~ except Exception as e:
            #~ _logger.warn('get repo: %s' %e)
        #~ return client.defaultRepository


    @api.multi
    def getFolder(self):
        self.ensure_one()
        return self.parent_id.getFolder() if self.parent_id else self.env['document.directory'].model2dir(self).getFolder()
        #~ return [a.parent_id.getFolder() if a.parent_id else self.env['document.directory'].model2dir(a).getFolder() for a in self][0]



    def cron_sync(self):
        repo = cmis_repo()
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
            repo = cmis_repo()
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
        return object_directory
        

    @api.multi
    def getFolder(self):
        self.ensure_one()
        return cmis_repo().getObject(self.remote_id).getFolder()

class res_users(models.Model):
    _inherit = "res.users"

    def init(self, cr):
        _logger.info("Init DB %s CMIS_LOGIN %s" % (cr.dbname,CMIS_LOGIN))

    def check_credentials(self, cr, uid, password):
        #~ if not password == config.get('admin_passwd',False) and uid not in CMIS_LOGIN.keys():  # admin_passwd overrides 
        global CMIS_CLIENT,CMIS_LOGIN,CMIS_SERVER
        
        if not CMIS_CLIENT:
            try:
                values = self.pool['ir.config_parameter'].get_param(cr,uid,'attachment_cmis.remote_server')
                CMIS_SERVER = values.split(',')[0]
                CMIS_CLIENT = CmisClient(CMIS_SERVER,values.split(',')[1],values.split(',')[2])
            except Exception as e:
                _logger.warn('CMIS_CLIENT: %s %s' %(e,values))
        if CMIS_CLIENT:
            if not cr.dbname in CMIS_LOGIN.keys():
                CMIS_LOGIN[cr.dbname] = {}
            if not uid in CMIS_LOGIN[cr.dbname].keys():
                CMIS_LOGIN[cr.dbname][uid] = {}
            CMIS_LOGIN[cr.dbname][uid]['password'] = password
            CMIS_LOGIN[cr.dbname][uid]['login'] = self.pool['res.users'].browse(cr,uid,uid).login
            try:
                CMIS_LOGIN[cr.dbname][uid]['client'] = CmisClient(CMIS_SERVER,CMIS_LOGIN[cr.dbname][uid]['login'],password)
            except Exception as e:
                _logger.warn('CMIS_LOGIN: %s %s %s' %(e,CMIS_SERVER,CMIS_LOGIN[cr.dbname][uid]['login']))
        _logger.warn('CMIS_CLIENT: %s CMIS_SERVER %s CMIS_LOGIN %s' %(CMIS_CLIENT,CMIS_SERVER,CMIS_LOGIN))
        return super(res_users, self).check_credentials(cr, uid, password)
