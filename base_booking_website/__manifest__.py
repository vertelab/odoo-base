# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Website Appointments',
    'version': '1.0',
    'category': 'Services/Appointment',
    'sequence': 215,
    'website': 'https://www.odoo.com/app/appointments',
    'description': """
Allow clients to Schedule Appointments through your Website
-------------------------------------------------------------

""",
    'depends': ['base_booking', 'website_partner'],
    'data': [
        # 'data/website_data.xml',
        # 'data/website_snippet_data.xml',
        'views/booking_templates.xml',
        'views/booking_type_views.xml',
        # 'views/appointment_invite_views.xml',
        # 'views/calendar_menus.xml',
        # 'views/appointment_templates_appointments.xml',
        # 'views/appointment_templates_registration.xml',
        # 'views/appointment_templates_validation.xml',
        # 'views/website_pages_views.xml',
        # 'views/snippets/s_appointments.xml',
        # 'views/snippets/s_appointments_preview_data.xml',
        # 'views/snippets/s_online_appointment.xml',
        # 'views/snippets/s_searchbar.xml',
        # 'views/snippets/snippets.xml',
        # 'security/calendar_security.xml',
        # 'security/ir.model.access.csv',
    ],
    # 'demo': [
    #     'data/appointment_demo.xml',
    # ],
    'installable': True,
    'auto_install': ['base_booking'],
    'license': 'OEEL-1',
    'assets': {
        'web.assets_frontend': [
            'base_booking_website/static/src/scss/website_calendar_ce.scss',
            'base_booking_website/static/src/js/website_calendar_ce.js'
        ],
        'web.assets_backend': [
            'base_booking_website/static/src/scss/booking_employee_url.scss',
            'base_booking_website/static/src/js/booking_employee_url.js'
        ],
        'website.assets_wysiwyg': [
            'base_booking_website/static/src/js/website_calendar.editor.js'
        ]
    }
}
