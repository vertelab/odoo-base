{
    'name': 'Partner KPI',
    'version': '12.0.1.1.3',						
    'category': '',
    'description': """
KPI \n
===========================================================\n
AFC-84\n
AFC-1788 - added new demo-data and fixed invisible tab for individuals\n
""",
    'author': 'Vertel AB',
    'license': 'AGPL-3',
    'website': 'http://www.vertel.se',
    'depends': [
        'base', 
        'partner_view_360'
    ],
    'data': [
	'views/res_partner_view.xml',
        'security/ir.model.access.csv'
        ],
    'demo': [
	'data/res.partner.kpi.csv'
        ],

    'application': False,
    'installable': True,
}
