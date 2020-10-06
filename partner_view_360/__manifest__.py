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
    'name': 'Partner 360 view',
    'version': '12.0.0.1.9',
    'category': '',
    'description': """
Module for employee 360 view
================================================================================================
This module alters, adds, removes and shuffles around fields in the partner view \n
Also adds new menus and views for partners of type jobseeker and employer \n
v12.0.0.1.4 AFC-102, 103, 140, 183, 192, 213, 210, 241, 259, 260, 346 \n
v12.0.0.1.5 AFC-713 Small changes in language \n
v12.0.0.1.6 AFC-713 Small changes in language \n
v12.0.0.1.7 AFC-713 Small changes in language \n
v12.0.0.1.9 AFC-816 Changed reload window to partern_360_view.\n
\n
""",
    'author': 'Vertel AB',
    'license': 'AGPL-3',
    'website': 'http://www.vertel.se',
    'depends': [
        'mail',
        'partner_firstname', 
        'contacts', 
        'res_ssyk',
        'res_sni',
        'partner_fax',
        'hr_office',
        'af_security',
        'res_drivers_license',
    ],
    'data': [
        'views/res_partner_template.xml',
        'views/res_partner_view.xml',
        #'wizard/res_partner_search_wizard.xml',
        #'security/ir.model.access.csv',
        "data/res.country.state.csv",
        "data/res.partner.skat.csv",
        "security/ir.model.access.csv"
    ],
    'demo': [
        "data/jobseekers/res.partner.csv",
        "data/employers/res.partner.csv",
    ],
    'qweb': [
        'static/src/xml/systray.xml',
    ],
    'application': False,
    'installable': True,
}
