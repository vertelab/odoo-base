# -*- coding: utf-8 -*-
{
    'name': 'Point of Sale Restaurant Booking',
'author': 'Vertel Sverige AB',
    'version': '18.0.1.0.0',
    'category': 'Sales/Point of Sale',
    'sequence': 6,
    'summary': 'This module lets you manage online reservations for restaurant tables.',
    'description': '''
Point of Sale Restaurant Booking
================================

    This module lets you manage online reservations for restaurant tables.

    Features:

        - UI Integration: Extends 3 view(s) in the Odoo interface.
        - Extends Odoo: Builds on booking.resource, calendar.event, pos.config, pos.session.
    ''',
    'website': 'https://vertel.se/apps/odoo-base/pos_restaurant_booking',
    'depends': ['base_booking', 'pos_restaurant'],
    'data': [
        'views/calendar_event_views.xml',
        'views/pos_restaurant_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'demo': [
        'demo/pos_restaurant_booking_demo.xml',
    ],
    'license': 'AGPL-3',
    'post_init_hook': '_pos_restaurant_booking_after_init',
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_restaurant_booking/static/src/**/*',
        ],
    }
}
