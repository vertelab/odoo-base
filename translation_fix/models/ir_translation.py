# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Yannick Vaucher
#    Copyright 2013 Camptocamp SA
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
from openerp.http import request
from openerp.osv import fields, osv


import logging
_logger = logging.getLogger(__name__)

class ir_translation(osv.osv):
    _inherit = "ir.translation"

    # _logger.warn('Translation fix loaded')

    def _set_src(self, cr, uid, id, name, value, args, context=None):
    	return super(ir_translation, self)._set_src(cr, uid, id, name, value, args, context=None)

    def _get_src(self, cr, uid, ids, name, arg, context=None):
        ''' Get source name for the translation. If object type is model then
        return the value store in db. Otherwise return value store in src field
        '''
        if context is None:
            context = {}
        res = dict.fromkeys(ids, False)
        for record in self.browse(cr, uid, ids, context=context):
            if record.type != 'model':
                res[record.id] = record.src
            else:
                model_name, field = record.name.split(',')
                model = self.pool.get(model_name)
                if model is not None:
                    # Pass context without lang, need to read real stored field, not translation
                    context_no_lang = dict(context, lang=None)
                    result = model.read(cr, uid, [record.res_id], [field], context=context_no_lang)
                    res[record.id] = result[0][field] if result and (field in result[0]) else False
                    if result and (field not in result[0]):
                        _logger.warn('Error in translation term with id: %s' % record.id)

        return res

    _columns = {
        'source': fields.function(_get_src, fnct_inv=_set_src, type='text', string='Source'),
        }
