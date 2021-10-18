# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution, third party addon
#    Copyright (C) 2004-2021 Vertel AB (<http://vertel.se>).
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
    'version': '12.0.0.3.11',
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
v12.0.0.1.10 AFC-704 Changed target for "Close-button".\n
v12.0.0.1.12 AFC-1890 fixed ssn field \n
v12.0.0.1.13 AFC-1910 changed order to state code and name. \n
v12.0.0.1.14 AFC-1914 fixed behaviour of zip field  \n
v12.0.0.2.1 AFC-1937: Added support for c/o addresses. \n
v12.0.0.2.2 AFC-1988: Better handling of bankid approvals. \n
v12.0.0.2.3 AFC-2072: Removed field eidentification from views. \n
v12.0.0.2.4 AFC-2097: Misc bugfixes. \n
v12.0.0.2.5 AFC-2168: Changed menu groups. \n
v12.0.0.2.6 AFC-2161: Removed state from some address views. \n
v12.0.0.2.7 AFC-2161: Removed thumbnail image for addresses. \n
v12.0.0.2.8 AFC-2229: made segment_jobseeker visible for users \n
v12.0.0.2.9 AFC-2239: Fixed jobseeker view.\n
v12.0.0.3.0 AFC-1950: Replaced kromtype with match_area.\n
v12.0.0.3.1 AFC-2372: Hide fields e-legitimation and arbetsökandesegment.\n
v12.0.0.3.2 AFC-2245: Added new field is_spu to mark problematic records.\n
v12.0.0.3.3 AFC-2305: Added css class to h1 tag\n
v12.0.0.3.4 AFC-1950: Removed KROM Rusta och matcha.\n
v12.0.0.3.5 AFC-2266: Updated format of person number for searching.\n
v12.0.0.3.6 AFC-2263: Changed boolean to selection field.\n
v12.0.0.3.7 AFC-2356: Added field has_address_co for displaying C/O prefix.\n
v12.0.0.3.8 AFC-2256: Signature in brackets.\n
v12.0.0.3.9 AFC-2489: Placed field under label for better reading.\n
v12.0.0.3.10 AFC-2712: Changed segment_jobseeker field \n
v12.0.0.3.11 AFC-2714: Split the text into a customer image for better readability \n
""",
    'author': 'Vertel AB',
    'license': 'AGPL-3',
    'website': 'http://www.vertel.se',
    'depends': [
        'mail',
        'partner_firstname',
        'contacts',
        'partner_ssn',
        'res_ssyk',
        'res_sni',
        'partner_fax',
        'hr_office',
        'af_security',
        'res_sun',
        'l10n_se',
        'partner_co_address'
    ],
    'data': [
        'views/res_partner_template.xml',
        'views/res_partner_view.xml',
        "data/res.partner.skat.csv",
        "security/ir.model.access.csv"
    ],
    'application': False,
    'installable': True,
}
