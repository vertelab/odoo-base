# -*- coding: utf-8 -*-
{
    'name': 'Matomo Website Analytics',
    'version': '18.0.1.0.0',
    'category': 'Marketing',
    'summary': 'Matomo integration for website analytics',
    'description': """
        Matomo Website Analytics
        ========================
        Concrete implementation of website analytics using Matomo.

        Features:
        - Fetch analytics data from Matomo API
        - Support for multiple sites
        - Page tracking
        - Traffic source tracking
    """,
    'author': 'Vertel Sverige AB',
    'website': 'https://vertel.se',
    'depends': ['base_serp'],
    'data': [
        'data/website_analytics_provider_data.xml',
        'data/website_analytics_report_data.xml',

        'views/website_analytics_report_type_views.xml',
        'views/templates.xml',
    ],
    'external_dependencies': {
        'python': ['requests'],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'AGPL-3',
}