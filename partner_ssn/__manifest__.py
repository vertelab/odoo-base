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

{
    'name': 'Partner Social Security Number',
    'version': '12.0.0.1.2',
    'category': '',
    'description': """
Adds social security number to partners
v12.0.0.1.1 AFC-2255 Changed the text when a person is older than 67 years old \n
v12.0.0.1.2 AFC-2186 Added Gender inside Contacts based on SSN's last number. \n
================================================================================================

""",
    'author': 'Vertel AB',
    'license': 'AGPL-3',
    'website': 'http://www.vertel.se',
    'depends': [
        'contacts',
    ],
    'data': [
        'views/res_partner_view.xml',
    ],
    'demo': [
        
    ],
    'application': False,
    'installable': True,
}
