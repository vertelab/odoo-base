# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) {year} {company} (<{mail}>)
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
    'name': 'Base: Security Classification',
    'version': '1.0',
    'summary': """
        Security Classification
    """,
    'category': '',
    'description': """
        Security Classification
    """,
    'author': 'Vertel AB',
    'website': 'https://vertel.se/apps/odoo-base',
    'license': 'AGPL-3',
    'depends': ["server_environment_data_encryption", "base"],
    'data': [
        "security/res_group.xml",
        "views/res_partner_views.xml",
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
