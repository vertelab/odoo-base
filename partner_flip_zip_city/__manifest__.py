{
    'name': 'Flip Partner Address',
    'version': '14.0.1.1.0',
    'category': '',
    'description': """
        Change place on City, State and Zip to Zip, City, State in the res-partner-form \n
		v14.0.1.1.0 Added translation \n
    """,
    'author': 'Vertel AB',
    'license': 'AGPL-3',
    'website': 'https://www.vertel.se',
    'depends': [
        'base',
    ],
    'data': [
        'views/res_partner_view.xml',
        'views/assets.xml',
    ],
    'application': False,
    'installable': True,
}
