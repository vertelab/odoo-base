# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-TODAY OpenERP S.A. <http://www.openerp.com>
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
import time

import logging
_logger = logging.getLogger(__name__)

class ir_cron(models.Model):
    _name = 'ir.cron'
    _inherit = 'ir.cron'

    @api.one
    def run_manually(self):
        start = time.time()
        super(ir_cron,self).run_manually()
        stop = time.time() - start
        (load_one,load_five,load_fifteen,tmp,tmp) = subprocess.check_output(['cat', '/proc/loadavg']).decode('utf-8').split()
        if self.log_type == 'all' or stop > 5.0:
            self.env['mail.message'].create({
                'body': 'Cron-job ready %s \nTime %s s\nLoad %s  %s (five) %s (fifteen)' % (self.name,stop,load_one,load_five,load_fifteen),
                'subject': '[cron] %s %s s' % (self.name,stop),
                'author_id': self._uid,
                'res_id': self.id,
                'model': self._name,
                'type': 'notification',})

            
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
