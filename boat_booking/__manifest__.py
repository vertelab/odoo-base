{
    'name': 'Website Product Map',
    'version': '18.0.1.0.0',
    'summary': "Booking of boats and other bookable resources.",
    'description': '''
Website Product Map
===================

    Booking of boats and other bookable resources.

    Features:

        - Web integration: Exposes HTTP endpoints for external systems.
        - UI Integration: Extends 5 view(s) in the Odoo interface.
        - Extends Odoo: Builds on booking.resource, booking.type, calendar.event, website.
    ''',
    'category': 'Sales',
    'author': "Vertel Sverige AB",
    'website': 'https://vertel.se/apps/odoo-base/boat_booking',
    'license': 'AGPL-3',
    "depends": ["base_booking", "website" , "base_booking_payment"],
    'demo': [
        "demo/boat_booking_demo.xml",
    ],
    "data": [
        "views/booking_resource_views.xml",
        "views/templates.xml",
        'demo/boat_booking_demo.xml',
        "views/calendar_event_view.xml",
        "views/website.xml",
        "views/booking_templates_registration.xml",
    ],
    'assets': {
        'web.assets_frontend': [
            # "boat_booking/static/src/js/map.js",
            # "boat_booking/static/src/js/boat_booking_slot_select.js",

            "boat_booking/static/src/scss/booking_map.scss",
            "boat_booking/static/src/js/appointment_select_appointment_slot.js",
            "boat_booking/static/src/xml/booking_resources_attributes.xml",
        ],
    },
    'installable': True,
    'auto-install': False,
    'application': True,
}
