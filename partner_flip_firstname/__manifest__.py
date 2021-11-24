{
    'name': 'Partner flip firstname',
    'version': '14.0.0.1.0',
    'category': '',
    'description': """
        Flips the position of the firstname and lastname fields on users and partners
    """,
    'author': 'Vertel AB',
    'license': 'AGPL-3',
    'website': 'https://www.vertel.se',
    'depends': [
        'partner_firstname',
    ],
    'data': [
        'views/res_partner_view.xml',
        'views/res_user_view.xml',
    ],
    'application': False,
    'installable': True,
}
