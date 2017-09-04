# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution, third party addon
#    Copyright (C) 2004-2017 Vertel AB (<http://vertel.se>).
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

from openerp import fields, api, models, _
import errno    
import os
import subprocess
from openerp.modules import get_module_resource, get_module_path

class knowledge_config_settings(models.Model):
    _inherit = 'knowledge.config.settings'
    directory_name = fields.Char(string='Directory Name',help="Directory where to save documents to be uploaded to the database")

    @api.multi
    def get_default_autoload(self):
        return {
            'directory_name': self.env['ir.config_parameter'].get_param('knowledge.directory_name'),
        }

    @api.one
    def set_default_autoload(self):
        if self.directory_name:        
            self.env['ir.config_parameter'].set_param('knowledge.directory_name',self.directory_name)
            try:
                os.makedirs(self.directory_name)
            except OSError as exc:
                if exc.errno == errno.EEXIST and os.path.isdir(self.directory_name):
                    pass
                else:
                    raise
            
            incron = subprocess.Popen(['incrontab','-l'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            (std,err) = incron.communicate()
            if err and 'is not allowed' in err:
                raise Warning(err)
            elif err and 'no table for' in err:
                pass
            elif not err:
                incron = subprocess.Popen(['incrontab','-r'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                (std,err) = incron.communicate()
                #~ raise Warning(get_module_path('attachment_autoload'),get_module_resource('attachment_autoload','bin/load_document.py'))
            echo = subprocess.Popen(['echo','%s IN_CREATE %s -D $@/$# -d %s' % (self.directory_name,get_module_resource('attachment_autoload','bin/load_document.py'),self.env.cr.dbname)],stdout=subprocess.PIPE)           
            incron = subprocess.Popen(['incrontab','-'],stdin=echo.stdout,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            echo.stdout.close()
            (std,err) = incron.communicate()
        else:
            self.env['ir.config_parameter'].set_param('knowledge.directory_name','Kalle')
            incron = subprocess.Popen(['incrontab','-r'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            (std,err) = incron.communicate()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
