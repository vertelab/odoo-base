# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo SA, Open Source Management Solution, third party addon
#    Copyright (C) 2024- Vertel Sverige AB (<https://vertel.se>).
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
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Base: Partner Enrich Base',
    'summary': "Base module for partner data enrichment.",
    'version': '18.0.1.1.0',
    'description': '''
Partner Enrich Base
===================

    Base module for Enrich Partner records with updated data. This module 
          does nothin but are a base fpr other enrichement modules

    Features:

        - UI Integration: Extends 1 view(s) in the Odoo interface.
        - Extends Odoo: Builds on existing Odoo models.
    ''',
    #'sequence': '1',
    'author': 'Vertel Sverige AB',
    'category': 'Technical',
    'website': 'https://vertel.se/apps/odoo-base/partner_enrich_base',
    'images': ['static/description/banner.png'], # 560x280 px.
    'license': 'AGPL-3',
    'contributor': '',
    'maintainer': 'Vertel Sverige AB',
    'repository': 'https://github.com/vertelab/odoo-base',
    'depends': ['partner_autocomplete','contacts'],
    'data': [
        'data/ir_action.xml',
    ],
    'application': False,
    'installable': True,
}
