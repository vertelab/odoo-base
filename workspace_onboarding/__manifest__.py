# -*- coding: utf-8 -*-
{
    'name': 'Kom igång med Vertel',
    'version': '18.0.1.0.0',
    'summary': 'Sammanhållande onboardingskurs: navigering, mobil och PWA',
    'description': """
Den första kursen: logga in, hitta rätt, installera appen och få en översikt över hela arbetsytan.
""",
    'author': 'Vertel AB',
    'website': 'https://vertel.se',
    'license': 'LGPL-3',
    'category': 'Website/eLearning',
    'depends': ['website_slides'],
    'data': [
        'views/slide_channel_data.xml',
    ],
    'demo': [
        'demo/slide_slide_demo.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
