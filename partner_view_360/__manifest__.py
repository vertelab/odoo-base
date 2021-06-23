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
    'name': 'Partner 360 view',
    'version': '12.0.0.1.5',
    'category': '',
    'author': 'Vertel AB',
    'license': 'AGPL-3',
    'website': 'http://www.vertel.se',
    'depends': [
        'contacts',
        'res_sun',
        'res_drivers_license',
        'res_ssyk',
        'res_sni',
        'partner_ssn',
        'l10n_se',
        'af_security'
    ],
    'data': [
        'views/res_partner_view.xml',
        'wizard/res_partner_search_wizard.xml',
        'security/ir.model.access.csv'
    ],
    'demo': [
        "data/jobseekers/res.partner.csv",
        "data/employers/res.partner.csv",
    ],
    'application': False,
    'installable': True,
}
