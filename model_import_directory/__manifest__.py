# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) {year} {company} info@vertel.se
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
#
# https://www.odoo.com/documentation/14.0/reference/module.html
#
{
    'name': 'Base: Model Import Directory',
    'version': '18.0.1.0.0',
    'summary': "Imports records from a directory of files.",
    'category': '', # Technical Settings|Localization|Payroll Localization|Account Charts|User types|Invoicing|Sales|Human Resources|Operations|Marketing|Manufacturing|Website|Theme|Administration|Appraisals|Sign|Helpdesk|Administration|Extra Rights|Other Extra Rights|
    'description': '''
Model Import Directory
======================

    Imports records from a directory of files.

    Features:

        - UI Integration: Extends 1 view(s) in the Odoo interface.
        - Extends Odoo: Builds on edi.message.
    ''',
    'author': 'Vertel Sverige AB',
    'website': 'https://vertel.se/apps/odoo-base/model_import_directory',
    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',
    'depends': ["base_setup", "edi_base"],
    'data': [
        "views/res_config_settings_views.xml",
        "data/edi_message_data.xml"
        ],
    'demo': [],
    'application': False,
    'installable': True,    
    'auto_install': False,
} 
