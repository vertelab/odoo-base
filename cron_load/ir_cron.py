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

from openerp import SUPERUSER_ID, netsvc, api
from openerp.osv import fields, osv

import logging
_logger = logging.getLogger(__name__)

class ir_cron(models.Model):
    _name = 'ir.cron'
    _inherit = ['ir.cron','mail.thread']

    
    log_type = fields.Selection([('all','All'),('loaded','Loaded')],string="Log Type",help="")

    def _process_job(self, job_cr, job, cron_cr):
        start = time.time()
        super(ir_cron,self)._process_job(job_cr, job, cron_cr)
        stop = time.time() - start
        (load_one,load_five,load_fifteen,tmp,tmp) = subprocess.check_output(['cat', '/proc/loadavg']).decode('utf-8').split()
        _logger.warn(job)
        # ~ env = Environment(cron_cr, job['user_id'], {})
        if job['log_type'] == 'all' or stop > 5.0:
            # ~ env['mail.message'].create({
            # ~ self.registry['mail.message'].create(cron_cr, job['user_id'], {
                # ~ 'body': 'Cron-job ready %s \nTime %s s\nLoad %s  %s (five) %s (fifteen)' % (job['name'], stop, load_one, load_five,load_fifteen),
                # ~ 'subject': '[cron] %s %s s' % (job['name'],stop),
                # ~ 'author_id': job['user_id'],
                # ~ 'res_id': job['id'],
                # ~ 'model': 'ir.cron',
                # ~ 'type': 'notification',})
            _logger.info('[cron] Cron-job ready %s Time %s s Load %s  %s (five) %s (fifteen)' % (job['name'], stop, load_one, load_five,load_fifteen))
            
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
