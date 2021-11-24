{
    'name': 'Flip Partner Address',
    'version': '14.0.0.1.0',
    'category': '',
    'description': """
        Change place on City, State and Zip to Zip, City, State in the res-partner-form
    """,
    'author': 'Vertel AB',
    'license': 'AGPL-3',
    'website': 'https://www.vertel.se',
    'depends': [
        'base',
    ],
    'data': [
        'views/res_partner_view.xml',
    ],
    'application': False,
    'installable': True,
}
