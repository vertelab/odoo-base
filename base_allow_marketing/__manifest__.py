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
    'name': 'Base Allow Marketing',
    'version': '1.0',
    'summary': """
        Opt-in for marketing email
    """,
    'category': 'Administration',
    'description': """
        Opt-in for marketing email
    """,
    'author': 'Vertel AB',
    'website': 'https://vertel.se/apps/odoo-',
    'images': ['static/description/banner.png'],  # 560x280
    'license': 'AGPL-3',
    'depends': ["auth_signup", "portal"],
    'data': [
        'views/signup_form_inherit.xml',
        'views/res_partner_form_inherit.xml',
        'views/res_users_form_inherit.xml',
        'views/portal_templates.xml',
    ],
    'demo': [],
    'application': False,
    'installable': True,
    'auto_install': False,
}
