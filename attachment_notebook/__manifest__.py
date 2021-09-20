# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution, third party addon
#    Copyright (C) 2004-2017 Vertel AB (<https://vertel.se>).
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
    'name': 'Attachment Notebook',
    'description': """
Attachment Notebook
===================

Adds a notebook for other modules to populate with more functionality
""",
    'version': '14.0.1',
    'category': 'Administration',
    'license': 'AGPL-3',
    'website': 'https://www.vertel.se',
    'author': 'Vertel AB',
    'depends': [],
    'data': [
        # 'views/document_templates.xml',
        'views/ir_attachment_view.xml',
    ],
    'application': False,
    'installable': True,
}
