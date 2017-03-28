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
from openerp import models, fields, api, _
from datetime import date, datetime, timedelta

import logging
_logger = logging.getLogger(__name__)

class mail_nodup(models.Model):
    _name = 'mail.nodup'

    recipient = fields.Char()
    subject  = fields.Char()
    date     = fields.Date(default=fields.Date.today())
    
    @api.model
    def check_dup(self, recipient, subject):
        dups = self.env['mail.nodup'].search([('recipient','=',recipient),('subject','=',subject),('date', '<=', fields.Date.to_string(date.today() - timedelta(days=int(self.env['ir.config_parameter'].get_param('mail_nodup days','7')))))])
        dups.unlink()
        dups = self.env['mail.nodup'].search([('recipient','=',recipient),('subject','=',subject)])
        if not dups:
            self.env['mail.nodup'].create({'recipient': recipient,'subject':subject})
            return False
        else:
            return True
    
    
