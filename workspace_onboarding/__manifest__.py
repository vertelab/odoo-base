# -*- coding: utf-8 -*-
{
    'name': 'Base: Kom igång med Vertel',
    'version': '18.0.2.0.0',
    'summary': 'Sammanhållande onboardingskurs: navigering, mobil och PWA',
    'description': """
Den första kursen: logga in, hitta rätt, installera appen och få en översikt över hela arbetsytan.

Fem sektioner: vad det är och varför, så kopplar du upp dig, så använder du
det i vardagen, mobilen i vardagen och ett manuellt test. Varje sektion
avslutas med ett quiz.
""",
    'author': 'Vertel Sverige AB',
    'website': 'https://vertel.se',
    'license': 'LGPL-3',
    'category': 'Website/eLearning',
    'depends': ['website_slides'],
    'data': [
        'views/slide_channel_data.xml',
        'data/slide_slides_s1.xml',
        'data/slide_slides_s2.xml',
        'data/slide_slides_s3.xml',
        'data/slide_slides_s4.xml',
        'data/slide_slides_s5.xml',
    ],
    'demo': [
        'demo/slide_slide_demo.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
