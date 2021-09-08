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
    'name': "Partner MQ/IPF-update dispatcher",
    'version': '12.0.0.3.2',
    'category': '',
    'description': """
Listen for updates on the MQ-bus
v12.0.0.3.0 - Changed sync to af_aisf_jobseeker__sync.
v12.0.0.3.1 AFC-2467: Implemented queue limit.
v12.0.0.3.2 AFC-2556: Added different requests to communicate with mq.

""",
    'author': 'Vertel AB',
    'license': 'AGPL-3',
    'website': 'http://www.vertel.se',
    'depends': ['base', 'calendar_af', 'af_aisf_jobseeker_sync'],
    'external_dependencies': {'python': ['stomp', 'xmltodict']},
    'data': ['data/cron.xml'],
    'application': False,
    'installable': True,
}
