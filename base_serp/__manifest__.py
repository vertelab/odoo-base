# -*- coding: utf-8 -*-
{
    'name': 'Base SERP Tracker',
    'version': '1.0.0',
    'category': 'Marketing',
    'summary': 'Track Search Engine Results Page (SERP) positions for domains and keywords',
    'description': """
Base SERP Tracker
=================
Track SERP (Search Engine Results Page) positions for multiple companies/domains across various keywords.

Features:
---------
* Track unlimited domains and keywords
* Multiple search engines support (Google by default)
* Provider-based architecture (BeautifulSoup default, extensible)
* Historical ranking data storage
* Scheduled tracking via cron jobs
* Multi-language support (Swedish, English)
* Graph-based reporting and analytics

Provider System:
----------------
* Pluggable provider architecture
* Default: BeautifulSoup (web scraping)
* Easily extend with additional providers (SerpAPI, etc.)
    """,
    'author': 'Vertel AB',
    'website': 'https://vertel.se',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'web',
    ],
    'external_dependencies': {
        'python': [
            'requests',
            'beautifulsoup4',
            'fake_useragent',
        ],
    },
    'data': [
        'security/ir.model.access.csv',
        'data/serp_provider_data.xml',
        'data/serp_cron.xml',
        'data/serp_actions.xml',
        'views/serp_provider_views.xml',
        'views/serp_result_views.xml',
        'views/serp_menu.xml',
        'views/res_partner_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}