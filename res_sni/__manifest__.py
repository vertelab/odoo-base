# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution, third party addon
#    Copyright (C) 2004-2017 Vertel AB (<http://vertel.se>).
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
    'name': 'Res SNI',
    'version': '14.0.0.2',
    'category': '',
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
    'author': 'Vertel AB',
    'website': 'http://www.vertel.se',
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
