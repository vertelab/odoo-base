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
    'name': 'Base: Enrich partner information from FöretagsAPI',
    'version': '18.0.1.0.0',
    'summary': 'Enrich partner with data from FöretagsAPI.se',
    'category': 'Website',
    'description': '''
Enrich partner information from FöretagsAPI
===========================================

    The module uses the official REST API at https://data.foretagsapi.se to
        fetch company information such as name, organisation number, address,
        SNI codes, business description, registration status and financial key
        figures. It also makes it possible to find other companies within the
        same SNI branch.

    Features:

        - UI Integration: Extends 2 view(s) in the Odoo interface.
        - Extends Odoo: Builds on foretagsapi.mapping.mixin, foretagssok.similar.wizard, foretagssok.similar.wizard.line.
    ''',
    'author': 'ARC Gruppen AB | Chrille Hedberg | https://arcgruppen.se | info@arcgruppen.se',
    'website': 'https://vertel.se/apps/odoo-base/partner_foretagssok',
    'license': 'AGPL-3',
    'contributor': '',
    'maintainer': 'Vertel Sverige AB',
    'repository': 'https://github.com/vertelab/odoo-base',
    'depends': [
        'partner_enrich_base',
        'partner_company_registry',
        'partner_sni',
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_actions_server.xml',
        'views/res_config_settings_views.xml',
        'views/res_partner_views.xml',
    ],
    'post_init_hook': 'post_init_hook',
    'application': False,
    'installable': True,
}
