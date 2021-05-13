{
    'name': 'Partner flip firstname',
    'version': '13.0.0.1.1',
    'category': '',
    'description': """
Flips the position of the OCA module partner_firstname's firstname and lastname fields
===========================================================
""",
    'author': 'Vertel AB',
    'license': 'AGPL-3',
    'website': 'http://www.vertel.se',
    'depends': [
        'partner_firstname',
    ],
    'data': [
			'views/res_partner_view.xml',
			'views/res_users_view.xml',
        ],
    'application': False,
    'installable': True,
}
