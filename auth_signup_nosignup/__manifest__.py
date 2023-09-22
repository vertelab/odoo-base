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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Auth Signup NoSignup",
    'summary': 'Removes new user signup from the front page',
    'author': 'Vertel AB',
    'images': ['static/description/banner.png'], # 560x280 px.
    'maintainer': 'Vertel AB',
    'category': 'Base',
    'version': '14.0.1.0.0',
    'license': 'AGPL-3',
    'website': 'https://vertel.se/apps/odoo-base/auth_signup_nosignup',
    'description': """    
    Removes new user signup from the front page.
    """,
    "depends": [
        "base",
        "auth_signup"
    ],
    "data": [
        'views/auth_signup_view.xml',
    ],
    "application": False,
    "installable": True,
}
