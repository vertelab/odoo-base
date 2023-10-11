# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo SA, Open Source Management Solution, third party addon
#    Copyright (C) 2021- Vertel AB (<https://vertel.se>).
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
    'name': 'Base: Export Records to XML',
    'version': '16.0.0.1.1',
    # Version ledger: 16.0 = Odoo version. 1 = Major. Non regressionable code. 2 = Minor. New features that are regressionable. 3 = Bug fixes
    'summary': 'Export Records to XML',
    'category': 'Technical',
    'description': """
        Export Records to XML - Models you can import include: \n
            - users
            - contacts
            - sale orders
            - events
            - hr employee
            - project/tasks
        \n 14.0.0.1.1 - Added Documentations
    """,
    'author': 'Vertel AB',
    'website': 'https://vertel.se/apps/odoo-base/record_export_to_xml',
    'images': ['static/description/banner.png'], # 560x280 px.
    'license': 'AGPL-3',
    'contributor': '',
    'maintainer': 'Vertel AB',
    'repository': 'https://github.com/vertelab/odoo-base.git',
    'depends': ['base', 'event', 'hr', 'sale', 'project'],
    'data': [
        "security/ir.model.access.csv",
        "views/export_view.xml",
        "data/data.xml",
    ],
    'installable': True,
    'auto_install': False,
}
