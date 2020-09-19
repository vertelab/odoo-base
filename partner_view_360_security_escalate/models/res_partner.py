# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution, third party addon
#    Copyright (C) 2004-2020 Vertel AB (<http://vertel.se>).
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
import logging
_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"  # odoo inheritance från res.partner

#  Grant temporary access to these jobseekers or set this user as responsible for the jobseeker            
    @api.multi
    def escalate_jobseeker_access(self,arendetyp, user):
        res = (250,'OK')
        for partner in self:
            res = super(ResPartner,self).escalate_jobseeker_access(arendetyp, user)
            res = self.env['edi.ace_errand'].escalate_jobseeker_access(partner,arendetyp,user)
        return res
        
            # ~ res = request.env['edi.ace_errand'].escalate_jobseeker_access(partner,post.get('arendetyp'))
            # ~ if res[0] != 250:  # OK
                # ~ return request.render('partner_view_360.403', {'error': 'ERROR: Escalate rights [%s] %s' % res, 'partner': partner, 'signatur':post.get('signatur')})

