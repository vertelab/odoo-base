# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution, third party addon
#    Copyright (C) 2020- Vertel AB (<http://vertel.se>).
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

{
    'name': 'Advanced Kanban',
    'version': '12.0.0.1',
    'category': '',
    'summary': "Makes it possible to perform any action when clicking a kanban card.",
    'description': """Advanced Kanban features
========================
Can redirect kanban cards to other actions. This is done by adding data-attributes to the kanban card (div with the oe_kanban_global_click class).
Example
-----------------------------------
This is built on the Contacts kanban (base.res_partner_kanban_view). It will open up all a partners sale orders when the card is clicked.

<div class="oe_kanban_global_click o_kanban_record_has_image_fill o_res_partner_kanban" data-kanban-adv-action-id="sale.act_res_partner_2_sale_order">

Available data-attributes
-------------------------
These are the data attributes that can currently be used. All domain and context attributes will be evaluated with the record object, just like the kanban card itself (seee the example).

* kanban-adv-action-id: The id of the action to perform (XML or database)
* kanban-adv-action-func: NOT WORKING YET. A name of a python function that returns the action
* kanban-adv-model: ACTION-ID METHOD ONLY. Overrides the model of the resulting action. Probably not useful and should be removed?
* kanban-adv-domain: ACTION-ID METHOD ONLY. Overrides the domain of the resulting action.
* kanban-adv-context: ACTION-ID METHOD ONLY. Overrides the domain of the resulting action.
* kanban-adv-action-context: ACTION-ID METHOD ONLY. Supplied when loading the action from action-id. Contains the active_id, active_ids, and active_model info. Not sure if this actually serves a purpose?
* kanban-adv-additional-context: Supplied when executing the action. Contains the active_id, active_ids, and active_model info.
* kanban-adv-target: Overrides the target of the resulting action.

Python method example
---------------------
NOT WORKING YET! Same example as up top, but done in python.
In the xml:

<div class="oe_kanban_global_click o_kanban_record_has_image_fill o_res_partner_kanban" data-kanban-adv-action-func="kanban_open_sale_orders">

And in python:

class Partner(models.Model):
    _inherit = 'res.partner'
    
    @api.multi
    def kanban_open_sale_orders(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window'].for_xml_id('sale', 'act_res_partner_2_sale_order')
        additional_context = {
            'active_id': self.id,
            'active_ids': self._ids,
            'active_model': 'res.partner'
        }
        return {
            'action': action,
            'additional_context': additional_context,
        }
""",
    'author': 'Vertel AB',
    'license': 'AGPL-3',
    'website': 'http://www.vertel.se',
    'depends': ['web',],
    'data': [
			'views/assets.xml',
        ],
    'application': True,
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4s:softtabstop=4:shiftwidth=4:
