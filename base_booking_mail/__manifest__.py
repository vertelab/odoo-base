# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) {year} {company} info@vertel.se
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
#
# https://www.odoo.com/documentation/14.0/reference/module.html
#
{
    'name': 'Base: Booking Mail',
    'version': '18.0.1.0.0',
    'summary': "Sends emails for bookings.",
    'category': '', # Technical Settings|Localization|Payroll Localization|Account Charts|User types|Invoicing|Sales|Human Resources|Operations|Marketing|Manufacturing|Website|Theme|Administration|Appraisals|Sign|Helpdesk|Administration|Extra Rights|Other Extra Rights|
    'description': '''
Booking Mail
============

    Sends emails for bookings.

    Features:

        - Automation: Scheduled jobs: Booking: Mail Scheduler.
        - UI Integration: Extends 3 view(s) in the Odoo interface.
        - Extends Odoo: Builds on booking.mail, booking.mail.calendar, booking.type, booking_mail_id.
    ''',
    'author': 'Vertel Sverige AB',
    'website': 'https://vertel.se/apps/odoo-base/base_booking_mail',
    'images': ['static/description/banner.png'], 
    'license': 'AGPL-3',
    'depends': ["base_booking"],
    'data': [
        "security/ir.model.access.csv",
        "views/booking_mail_views.xml",
        "views/booking_type_views.xml",
        "views/booking_menu_views.xml",
        "data/ir_cron_data.xml"
        ],
    'demo': [],
    'application': False,
    'installable': True,    
    'auto_install': False,
}
