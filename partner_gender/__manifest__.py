# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution, third party addon
#    Copyright (C) 2021- Vertel AB (<http://vertel.se>).
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
    'name': 'Partner Gender',
    'version': '14.0.0.1',
    'category': 'Customer Relationship Management',
    'summary': 'Adds a "Personal information" tab on res_partners with a gender field',
    'description': """
        Features:\n
        * Adds a "Personal information" tab on res_partners with a gender field\n
        * Adds an select box for gender on personal details form in the user portal\n
        This module is maintained from: https://github.com/vertelab/odoo-base/tree/14.0/partner_gender/\n
    """,
    'author': 'Vertel AB',
    'website': 'https://www.vertel.se',
    'depends': ['base'],
    'data': [
        'views/res_partner.xml',
        'views/templates.xml',
    ],
    'installable': True,
}
