# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution, third party addon
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
    'name': 'Daily notes',
    'version': '12.0.1.4.6',
    'category': '',
    'description': """
Daily notes
===============================================================================
AFC-81\n
AFC-1923\n
This module allows daily notes for a partner.\n
v12.0.1.1.0: Added mapping for Integration platform with the module base_map.\n
v12.0.1.4.0: Changed display Daily Notes types in "name in Tree-view".\n
v12.0.1.5.0 AFC-999: Removed duplicate translation line for Secret\n
v12.0.1.6.0: moved all generation of daily notes from calendar_af to this module\n
v12.0.1.7.0: Commented away the Smart-button on the contact-view-form\n
v12.0.1.2.0: Replaced the computed fields with normal fields because of changes in architecture\n
v12.0.1.2.1 AFC-1674: Replaced some normal fields with computed ones. \n
v12.0.1.2.2 AFC-1920: Added updates to next_contact fields when making new appointments. \n
v12.0.1.3.0 AFC-2155: Updated logic for how next_contact and last_contact are updated \n
12.0.1.4.0 AFC-2213: Fixed bug in next_contact calculation. Changed type of next_contact_date
and last_contact_date from Datetime to Date. \n
v12.0.1.4.1 AFC-2228: Made IPF meeting sync more robust. \n
v12.0.1.4.2 AFC-2137: Fixed behaviour of this code. \n
v12.0.1.4.3 AFC-2426: Fixed next appointment +2 hrs problem. \n
v12.0.1.4.4 AFC-2489: Placed field under label for better reading. \n
v12.0.1.4.5 stopped crashing on partners with no next or last contact date \n
v12.0.1.4.6 AFC-2297: Appointment notes now reflect (timezone correct) creation time \n

""",
    'author': 'Vertel AB',
    'license': 'AGPL-3',
    'website': 'http://www.vertel.se',
    'depends': [
        'partner_view_360',
        'calendar_af',
        'edi_af_aisf_trask',
    ],
    'data': [
            'security/ir.model.access.csv',
            'views/res_partner_notes_view.xml',
            'views/res_partner_view.xml',
            "data/res.partner.note.type.csv",

    ],
    'demo': [
            "data/res.partner.notes.csv",
    ],
    'application': False,
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4s:softtabstop=4:shiftwidth=4:
