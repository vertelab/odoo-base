{
    'name': 'Partner Design Mockup',
    'version': '12.0.0.2',
    'category': '',
    'description': """
    Download 'One Click Form Edit' module from here : \n
    https://apps.odoo.com/apps/modules/12.0/one_click_form_edit/\n
    V12.0.0.1 AFC-2170 - This module adds two different ways of displaying Odoo content. A normal formview with tabs and a custom view with different boxes with content-views. \n
    V12.0.0.2 AFC-2170 - Added search box in second type of view to search partners. \n
""",
    'author': 'Vertel AB',
    'license': 'AGPL-3',
    'website': 'http://www.vertel.se',
    'depends': [
        'crm', 'project',  'one_click_form_edit'
    ],
    'data': [
        'views/res_partner_views.xml',
        'wizard/search_partners_views.xml',
    ],
    'application': False,
    'installable': True,
}
