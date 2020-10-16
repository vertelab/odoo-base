# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution, third party addon
#    Copyright (C) 2004-2019 Vertel AB (<http://vertel.se>).
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
    'name': 'Daily notes',
    'version': '12.0.1.6',
    'category': '',
    'description': """
Daily notes
===============================================================================
AFC-81
This module allowes daily notes for a partner.
- 12.0.1.1  Added mapping for Integration platform with the module base_map.
- 12.0.1.4  Changed display Daily Notes types in "name in Tree-view".
- 12.0.1.5 AFC-999 Removed duplicate translation line for Secret
- 12.0.1.6 moved all generation of daily notes from calendar_af to this module
""",
    'author': 'Vertel AB',
    'license': 'AGPL-3',
    'website': 'http://www.vertel.se',
    'depends': [
        'base_map',
        'partner_view_360',
        'calendar_af'
    ],
    'data': [
            'security/ir.model.access.csv',
            'views/res_partner_notes_view.xml',
            'views/res_partner_view.xml',
            "data/res.partner.note.type.csv",

    ],
    'demo': [
            "data/res.partner.notes.csv",
    ],
    'application': False,
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4s:softtabstop=4:shiftwidth=4:
