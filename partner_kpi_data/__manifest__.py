{
    'name': 'Partner KPI',
    'version': '12.0.1.1',						
    'category': '',
    'description': """
KPI 
===========================================================
AFC-84
""",
    'author': 'Vertel AB',
    'license': 'AGPL-3',
    'website': 'http://www.vertel.se',
    'depends': ['base'],
    'data': [
			'views/res_partner.xml',
            'security/ir.model.access.csv'
        ],
    'application': False,
    'installable': True,
}