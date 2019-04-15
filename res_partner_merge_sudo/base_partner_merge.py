# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution, third party addon
#    Copyright (C) 2019 Vertel AB (<http://vertel.se>).
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
import logging
_logger = logging.getLogger(__name__)

class MergePartnerAutomatic(models.TransientModel):
    _inherit = 'base.partner.merge.automatic.wizard'
    
    @api.multi
    def merge_cb(self):
        return super(MergePartnerAutomatic, self.sudo()).merge_cb()
        # ~ assert is_integer_list(ids)

        # ~ context = dict(context or {}, active_test=False)
        # ~ this = self.browse(cr, uid, ids[0], context=context)

        # ~ partner_ids = set(map(int, this.partner_ids))
        # ~ if not partner_ids:
            # ~ this.write({'state': 'finished'})
            # ~ return {
                # ~ 'type': 'ir.actions.act_window',
                # ~ 'res_model': this._name,
                # ~ 'res_id': this.id,
                # ~ 'view_mode': 'form',
                # ~ 'target': 'new',
            # ~ }

        # ~ self._merge(cr, uid, partner_ids, this.dst_partner_id, context=context)

        # ~ if this.current_line_id:
            # ~ this.current_line_id.unlink()

        # ~ return self._next_screen(cr, uid, this, context)
