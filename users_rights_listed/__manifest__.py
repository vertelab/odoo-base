##############################################################################
#
#    OpenERP, Open Source Management Solution, third party addon
#    Copyright (C) 2004-2021 Vertel AB (<http://vertel.se>).
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
    'name': 'Users Rights Listed',
    'version': '14.0.0.0.1',
    'category': '',
    'summary': 'Adds a UserGroup field to the res_users tree-view in debug-mode.',
    'description': """
        Adds a UserGroup field to the res_users tree-view in debug-mode.\n
        This module is maintained from: https://github.com/vertelab/odoo-base/edit/14.0/users_rights_listed/ \n
""",
    'author': "Vertel AB",
    'license': "AGPL-3",
    'website': 'https://www.vertel.se',
    'depends': [],
    'data': [
        "views/usergroup.xml"
    ],
    'installable': True,
}
