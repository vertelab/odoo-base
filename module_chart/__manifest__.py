# -*- coding: utf-8 -*-
################################################################################
#
#    OpenERP, Open Source Management Solution
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################

{
    'name': 'Base Module depends Chart',
    'version': '14.0.1.0.0',
    'category': 'Tools',
    'description': """This module adds a graphical description of the Odoo database dependencys.\n
	Install it and go to Apps -> Module Graph to see a dynamic map of the installed modules.\n-development\n
	This module is maintained from: https://github.com/vertelab/odoo-base/ \n
	""",
    'author': "Vertel AB",
    'license': 'AGPL-3',
    'website': 'https://www.vertel.ab',
	'contributors': 'Vertel AB, N-Development',
	'maintainers': 'Vertel AB',
    'depends': [
        'base',
        'web',
    ],
    'data': [
        'views/assets.xml',
        'views/ir_module.xml',
    ],
    'qweb': [
        'static/src/xml/module_graph.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    "application": False,
}
