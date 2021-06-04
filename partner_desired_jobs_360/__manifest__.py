# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution, third party addon
#    Copyright (C) 2004-2019 Vertel AB (<http://vertel.se>).
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
    'name': 'Partner desired jobs 360',
    'version': '12.0.1.3',
    'category': '',
    'description': """
Module to see which jobs a jobseeking partner desires
================================================================================================
AFC-1753 fixed a domain
AFC-1849 made some fields debug only
V12.0.1.3 AFC-2421 Added Occupation demand's fields in Desired job tab.
""",
    'author': 'Vertel AB',
    'license': 'AGPL-3',
    'website': 'http://www.vertel.se',
    'depends': ['partner_view_360', 'partner_desired_jobs'],
    'data': [
        'views/res_partner_view.xml',
    ],
    'application': False,
    'installable': True,
}
