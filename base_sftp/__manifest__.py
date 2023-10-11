# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo SA, Open Source Management Solution, third party addon
#    Copyright (C) 2022- Vertel AB (<https://vertel.se>).
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
    'name': 'Base: SFTP',
    'version': '14.0.1.0.0',
    'summary': 'Access your documents via SFTP.',
    'category': 'Technical',
    'description': """
    The base SFTP connects with ir.attachments.
    """,
    'author': 'Vertel AB',
    'website': 'https://vertel.se/apps/odoo-base/base_sftp',
    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',
    'contributor': '',
    'maintainer': 'Vertel AB',
    'repository': 'https://github.com/vertelab/odoo-base',
    'depends': ['base', 'mail'],
    'data': [
        "data/ir_config_parameter.xml",
        # "views/ir_config_view.xml",
    ],
    "external_dependencies": {
        'python': ['paramiko'],
    },
    "auto_install": False
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
