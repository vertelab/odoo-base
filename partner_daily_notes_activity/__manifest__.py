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
    'name': 'Partner Daily Notes Activity - DEPRECIATED',
    'version': '12.0.1.2',
    'category': '',
    'description': """
Partner Daily Notes Activity
===============================================================================
AFC-649 
This module shows daily notes activities for a partner.
- 12.0.1.1  Added a Smart button on the contact-card that displays "Number of records for that user in the Daily Notes".
- 12.0.1.2  Changed view for the expath to link in to.
""",
    'author': 'Vertel AB',
    'license': 'AGPL-3',
    'website': 'http://www.vertel.se',
    'depends': [
        'partner_daily_notes',
        'partner_view_360',
        'base'

    ],
    'data': [
        # 'views/res_partner_view.xml'

        ],
    'application': False,
    'installable': False,
}
# vim:expandtab:smartindent:tabstop=4s:softtabstop=4:shiftwidth=4:
