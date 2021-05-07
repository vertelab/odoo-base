{
    'name': 'Partner Design Mockup',
    'version': '12.0.0.1',
    'category': '',
    'description': """
    V12.0.0.1 AFC-2170 - This module adds two different ways of displaying Odoo content. A normal formview with tabs and a custom view with different boxes with content-views. \n
""",
    'author': 'Vertel AB',
    'license': 'AGPL-3',
    'website': 'http://www.vertel.se',
    'depends': [
        'crm', 'project'
    ],
    'data': [
        'views/res_partner_views.xml',
        'wizard/search_partners_views.xml',
    ],
    'application': False,
    'installable': True,
}
