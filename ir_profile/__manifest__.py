# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'IR Profile',
    'version': '14.0.0.1',
    'category': 'Hidden',
    'description': """
The kernel of Odoo, needed for all installation.
===================================================
""",
    'depends': ['base_setup'],
    'data': [
        'views/ir_profile_views.xml',
        'views/res_config_settings_views.xml',
        'views/speedscope_template.xml',
    ],
    'qweb': ['ir_profile/static/src/xml/*.xml'],
    'assets': {
        'web.assets_backend': [
            'ir_profile/js/profiling_qweb_view.js',
        ]
    },
    'installable': True,
    'auto_install': True,
    'license': 'LGPL-3',
}
