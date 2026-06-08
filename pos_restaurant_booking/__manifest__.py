# -*- coding: utf-8 -*-
{
    'name': 'Point of Sale Restaurant Booking',
    'version': '1.0',
    'category': 'Sales/Point of Sale',
    'sequence': 6,
    'summary': 'This module lets you manage online reservations for restaurant tables',
    'website': 'https://www.vertelab.se',
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
