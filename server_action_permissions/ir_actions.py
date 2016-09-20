# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution, third party addon
#    Copyright (C) 2004-2016 Vertel AB (<http://vertel.se>).
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

import logging
_logger = logging.getLogger(__name__)



class ir_actions_server(models.Model):
    _inherit = 'ir.actions.server'
    
    groups_id = fields.Many2many('res.groups', string='Groups')


EXCLUDED_FIELDS = set((
    'report_sxw_content', 'report_rml_content', 'report_sxw', 'report_rml',
    'report_sxw_content_data', 'report_rml_content_data', 'search_view', ))
    
ACTION_SLOTS = [
                "client_action_multi",  # sidebar wizard action
                "client_print_multi",   # sidebar report printing button
                "client_action_relate", # sidebar related link
                "tree_but_open",        # double-click on item in tree view
                "tree_but_action",      # deprecated: same as tree_but_open
               ]


class ir_actions_server(models.Model):
    _inherit = 'ir.actions.server'
    
    groups_id = fields.Many2many('res.groups', string='Groups')
    
class ir_values(models.Model):
    _inherit = 'ir.values'
    
    

    def get_actions(self, cr, uid, action_slot, model, res_id=False, context=None):
        """Retrieves the list of actions bound to the given model's action slot.
           See the class description for more details about the various action
           slots: :class:`~.ir_values`.

           :param string action_slot: the action slot to which the actions should be
                                      bound to - one of ``client_action_multi``,
                                      ``client_print_multi``, ``client_action_relate``,
                                      ``tree_but_open``.
           :param string model: model name
           :param int res_id: optional record id - will bind the action only to a
                              specific record of the model, not all records.
           :return: list of action tuples of the form ``(id, name, action_def)``,
                    where ``id`` is the ID of the default entry, ``name`` is the
                    action label, and ``action_def`` is a dict containing the
                    action definition as obtained by calling
                    :meth:`~openerp.osv.osv.osv.read` on the action record.
        """
        assert action_slot in ACTION_SLOTS, 'Illegal action slot value: %s' % action_slot
        # use a direct SQL query for performance reasons,
        # this is called very often
        query = """SELECT v.id, v.name, v.value FROM ir_values v
                   WHERE v.key = %s AND v.key2 = %s
                        AND v.model = %s
                        AND (v.res_id = %s
                             OR v.res_id IS NULL
                             OR v.res_id = 0)
                   ORDER BY v.id"""
        cr.execute(query, ('action', action_slot, model, res_id or None))
        results = {}
        for action in cr.dictfetchall():
            if not action['value']:
                continue    # skip if undefined
            action_model_name, action_id = action['value'].split(',')
            if action_model_name not in self.pool:
                continue    # unknow model? skip it
            action_model = self.pool[action_model_name]
            fields = [field for field in action_model._fields if field not in EXCLUDED_FIELDS]
            # FIXME: needs cleanup
            try:
                action_def = action_model.read(cr, uid, int(action_id), fields, context)
                if action_def:
                    if action_model_name in ('ir.actions.report.xml', 'ir.actions.act_window','ir.actions.server'):  # server action added
                        groups = action_def.get('groups_id')
                        if groups:
                            cr.execute('SELECT 1 FROM res_groups_users_rel WHERE gid IN %s AND uid=%s',
                                       (tuple(groups), uid))
                            if not cr.fetchone():
                                if action['name'] == 'Menuitem':
                                    raise osv.except_osv('Error!',
                                                         'You do not have the permission to perform this operation!!!')
                                continue
                # keep only the first action registered for each action name
                results[action['name']] = (action['id'], action['name'], action_def)
            except except_orm:
                continue
        return sorted(results.values())


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
