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
    'name': 'Base: Res SNI',
    'version': '14.0.0.0.2',
    # Version ledger: 14.0 = Odoo version. 1 = Major. Non regressionable code. 2 = Minor. New features that are regressionable. 3 = Bug fixes
    'summary': 'SNI Swedish Standard Industrial Classification.',
    'category': 'Technical',
    'description': """
SNI Swedish Standard Industrial Classification
==============================================
Industry classification or industry taxonomy is a type of economic taxonomy that organizes companies into industrial groupings based on similar production processes, similar products, or similar behavior in financial markets.

The SNI standard is modeled on the Statistical Classification of Economic Activities in the European Community, commonly referred to as NACE. The SNI standard is maintained by Statistics Sweden (also known as SCB), a Swedish government office

SNI 2007

The Standard Industrial Classification (SIC) is a system for classifying industries by a four-digit code. Established in the United States in 1937, it is used by government agencies to classify industry areas. The SIC system is also used by agencies in other countries, e.g., by the United Kingdom's Companies House.
Standard Industrial Classification - Wikipedia
https://en.wikipedia.org/wiki/Standard_Industrial_Classification


Industry classification or industry taxonomy is a type of economic taxonomy that organizes companies into industrial groupings based on similar production processes, similar products, or similar behavior in financial markets.

SNI Swedish Standard Industrial Classification

https://en.wikipedia.org/wiki/Swedish_Standard_Industrial_Classification

v12.0.0.2 Added automatic install of the codes.
AFC-156
""",
    #'sequence': '1',
    'author': 'Vertel AB',
    'website': 'https://vertel.se/apps/odoo-base/res_sni',
    'images': ['static/description/banner.png'], # 560x280 px.
    'license': 'AGPL-3',
    'contributor': '',
    'maintainer': 'Vertel AB',
    'repository': 'https://github.com/vertelab/odoo-base.git',
    'depends': ['contacts',],
    'data': [
        'views/res_partner_view.xml',
        'security/ir.model.access.csv',
        'views/res_sni_view.xml',
		'data/res.sni.csv',
    ],
    'application': False,
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4s:softtabstop=4:shiftwidth=4:
