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
    'name': 'Partner 360 view',
    'version': '12.0.0.1.1',
    'category': '',
    'description': """
Module for employee 360 view
================================================================================================
This module alters, adds, removes and shuffles around fields in the partner view 
AFC-102, 103, 140, 183, 192, 213, 210
""",
    'author': 'Vertel AB',
    'license': 'AGPL-3',
    'website': 'http://www.vertel.se',
    'depends': ['contacts'],
    'data': [
			'views/res_partner_view.xml',
        ],
    'demo': [
            "data/arbetssokande/res.partner.csv",
            "data/arbetsgivare/res.partner.csv",
    ],

    'application': False,
    'installable': True,
}
