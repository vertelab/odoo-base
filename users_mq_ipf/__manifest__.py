# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution, third party addon
#    Copyright (C) 2004-2020 Vertel AB (<http://vertel.se>).
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
    'name': "Users MQ/IPF-update dispatcher",
    'version': '12.0.0.3.1',
    'category': '',
    'description': """

v12.0.0.1.1 - added logging with af_process_log, refactored code
v12.0.0.2.0 - AFC-2408: added call to x500 when creating new users.
v12.0.0.3.0 - AFC-2409: added call to ASH KOM when creating offices and improved x500 call.
v12.0.0.3.1 - AFC-2543: removed some logging.
""",
    'author': 'Vertel AB',
    'license': 'AGPL-3',
    'website': 'http://www.vertel.se',
    'depends': ['base', 'hr_office', 'af_process_log', 'edi_af_officer'],
    'external_dependencies': {'python': ['stomp']},
    'data': ['data/cron.xml'],
    'application': False,
    'installable': True,
}
