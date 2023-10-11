# -*- coding: utf-8 -*-
################################################################################
#
#    Odoo SA, Open Source Management Solution
#    Copyright (C) 2019 N-Development (<https://n-development.com>).
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
################################################################################

{
    'name': 'Base: Module Chart',
    'version': '16.0.1.0.0',
    # Version ledger: 16.0 = Odoo version. 1 = Major. Non regressionable code. 2 = Minor. New features that are regressionable. 3 = Bug fixes
    'summary': 'Adds a graphical description of the Odoo database dependencies.',
    'category': 'Tools',
    'description': """
    This module adds a graphical description of the Odoo database dependencies.
	Install it and go to Apps -> Module Graph to see a dynamic map of the installed modules.
	This module is maintained from: https://github.com/vertelab/odoo-base/
	""",
    #'sequence': '1',
    'author': 'Vertel AB',
    'website': 'https://vertel.se/apps/odoo-base/module_chart',
    'images': ['static/description/banner.png'], # 560x280 px.
    'license': 'AGPL-3',
    'contributor': 'Vertel AB, N-Development',
    'maintainer': 'Vertel AB',
    'repository': 'https://github.com/vertelab/odoo-base.git',
    'depends': ['base','web', ],
    'data': [
        'views/assets.xml',
        'views/ir_module.xml',
    ],
    'qweb': [
        'static/src/xml/module_graph.xml',
    ],
    'installable': True,
    "application": False,
}
