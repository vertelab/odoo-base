{
    'name': 'Website Product Map',
    'version': '18.0.1.0',
    'summary': "",
    'description': """Allows visualization of map on odoo website""",
    'category': 'Sales',
    'author': "Vertel AB",
    'website': "https://www.vertel.se",
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
