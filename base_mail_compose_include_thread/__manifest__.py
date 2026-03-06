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
    'name': 'Base: Mail Compose Include Thread',
    'version': '14.0.1.0.0',
    'summary': 'Mail Compose Include Thread',
    'category': '',
    'author': 'Vertel AB',
    'website': 'https://vertel.se/apps/odoo-base/base_mail_compose_include_thread',
    'images': ['static/description/banner.png'],  # 560x280 px.
    'license': 'AGPL-3',
    'contributor': '',
    'maintainer': 'Vertel AB',
    'repository': 'https://github.com/vertelab/odoo-base',
    "description": """
        Mail Compose Include Thread.
    """,
    'depends': ['base', 'mail'],
    "data": [
        'views/mail_compose_message_view.xml',
    ],
    "application": False,
    "installable": True,
}
