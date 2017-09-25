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
from openerp.exceptions import except_orm, Warning, RedirectWarning
from datetime import datetime

import logging
_logger = logging.getLogger(__name__)


class ProfileModel(models.TransientModel):
    _name = 'profile.model'

    object_id = fields.Reference(selection=[], string='Model', required=True)
    profile_fields = fields.One2many(comodel_name='profile.model.field', inverse_name='profile_id', compute='_profile_fields')
    
    @api.one
    @api.depends('object_id')
    @api.onchange('object_id')
    def _profile_fields(self):
        self.profile_fields = self.env['profile.model.field'].browse()
        res = []
        if not self.object_id:
            return
        for field in self.object_id.fields_get():
            start = datetime.now()
            self.object_id.read([field])
            dt = datetime.now() - start
            res.append((float(dt.seconds) + float(dt.microseconds) / 1000000, field))
        res.sort(key=lambda f: f[0], reverse=True)
        for f in res:
            self.profile_fields |= self.env['profile.model.field'].create({
                'field': f[1],
                'time': f[0],
            })

    @api.model
    def profile(self, model, id):
        _logger.warn('\n\nmodel: %s\nids: %s\n\n' % (model, id))
        profile = self.create({'object_id' : '%s,%s' % (model, id)})
        return {
                    'res_model': 'profile.model',
                    'res_id': profile.id,
                    'views': [[False, 'form']],
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'target': 'new',
                    'context': {},
                }

class ProfileModelfield(models.TransientModel):
    _name = 'profile.model.field'
    
    profile_id = fields.Many2one('profile.model')
    field = fields.Char(string='Field')
    time  = fields.Float(string='Time (s)', digits=(10, 6))
