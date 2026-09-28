# -*- coding: utf-8 -*-
{
    'name': 'Base: Booking Payment',
'author': 'Vertel Sverige AB',
    'website': 'https://vertel.se/apps/odoo-base/base_booking_payment',
    'version': '18.0.1.0.0',
    'category': 'Booking',
    'summary': 'Booking payment.',
    'description': '''
Booking payment
===============

    Booking payment.

    Features:

        - Web integration: Exposes HTTP endpoints for external systems.
        - UI Integration: Extends 9 view(s) in the Odoo interface.
        - Extends Odoo: Builds on account.move, booking.answer.input, booking.resource, booking.type.
    ''',
    'license': 'AGPL-3',
    'depends': ['base_booking', 'account_payment'],
    'data': [
        'security/ir.model.access.csv',
        #'views/booking_answer_input_views.xml',
        'views/booking_templates_appointments.xml',
        'views/booking_templates_payment.xml',
        'views/booking_templates_registration.xml',
        'views/booking_templates_validation.xml',
        'views/booking_type_views.xml',
        'views/calendar_booking_templates.xml',
        'views/calendar_booking_views.xml',
        'views/booking_resource_views.xml',
    ],
    #'assets': {
    #    'web.assets_frontend': [
    #        'appointment_account_payment/static/src/scss/appointment_payment.scss',
    #    ],
    #}
}
