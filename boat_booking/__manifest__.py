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
        'demo/boat_booking_demo.xml'
    ],
    'assets': {
        'web.assets_frontend': [
            "boat_booking/static/src/js/map.js",
            "boat_booking/static/src/scss/booking_map.scss",
        ],
        # "web.assets_backend": [
        #     "boat_booking/static/src/xml/google_map_field.xml",
        #     "boat_booking/static/src/scss/google_map_field.scss",
        #     "boat_booking/static/src/js/google_map_field.js",
        #     "boat_booking/static/src/js/google_api_services.js",
        #     "boat_booking/static/src/js/config.js",
        # ],
    },
    'installable': True,
    'auto-install': False,
    'application': True,
}
