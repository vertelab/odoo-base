# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Bookings: ',
    'version': '1.3',
    'category': 'Booking/Appointment',
    'sequence': 215,
    'summary': 'A base module to allow booking integrations in any flow',
    'website': 'https://www.odoo.com/app/appointments',
    'description': """
A base module to allow booking integrations in any flow
    """,
    'depends': ['calendar', 'phone_validation', 'portal', 'resource', 'mail'],
    'data': [
        # 'data/calendar_data.xml',
        # 'data/mail_message_subtype_data.xml',
        # 'data/mail_template_data.xml',
        # 'data/resource_calendar_data.xml',
        'security/res_groups_data.xml',
        # 'security/ir_rule_data.xml',
        'security/ir.model.access.csv',
        'views/calendar_views.xml',
        'views/calendar_alarm_views.xml',
        'views/calendar_event_views.xml',
        'views/booking_invite_views.xml',
        'views/booking_type_views.xml',
        'views/booking_resource_views.xml',
        'views/booking_slot_views.xml',
        # 'views/resource_calendar_leaves_views.xml',
        'views/booking_menus.xml',
        # 'views/calendar_menus.xml',
        'views/booking_templates.xml',
        'views/booking_templates_registration.xml',
        'views/booking_templates_validation.xml',
        'views/portal_templates.xml',
        # 'wizard/booking_manage_leaves.xml',
    ],
    # 'demo': [
    #     'data/res_partner_demo.xml',
    #     'data/appointment_type_demo.xml',
    #     'data/appointment_resource_demo.xml',
    # ],
    'installable': True,
    'application': True,
    'license': 'OEEL-1',
    'assets': {
        'web.assets_frontend': [
            # 'mail/static/src/utils/common/format.js',
            'base_booking/static/src/js/utils.js',
            'base_booking/static/src/scss/appointment.scss',
            'base_booking/static/src/js/appointment_select_appointment_type.js',
            'base_booking/static/src/js/appointment_select_appointment_slot.js',
            'base_booking/static/src/js/appointment_validation.js',
            'base_booking/static/src/js/appointment_form.js',
            'base_booking/static/src/xml/*.xml',
        ],
        'web.assets_backend': [
            'base_booking/static/src/scss/appointment_type_views.scss',
            'base_booking/static/src/scss/web_calendar.scss',
            # 'base_booking/static/src/views/**/*',
        #     ('remove', 'appointment/static/src/views/gantt/**'),
            'base_booking/static/src/components/**/*',
        #     'base_booking/static/src/js/appointment_insert_link_form_controller.js',
        #     'base_booking/static/src/appointment_plugin.js',
        ],
        'web_editor.backend_assets_wysiwyg': [
            'base_booking/static/src/js/wysiwyg.js',
        ],
    }
}
