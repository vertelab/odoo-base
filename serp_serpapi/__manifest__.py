# -*- coding: utf-8 -*-
{
    'name': 'SERP SerpAPI Integration',
    'version': '1.0.0',
    'category': 'Marketing',
    'summary': 'SerpAPI provider for reliable SERP tracking',
    'description': """
SERP SerpAPI Integration
========================
Adds SerpAPI provider to the base SERP tracking module.

Features:
---------
* Reliable Google search results
* No blocking or CAPTCHA issues
* Production-ready solution
* Easy API key configuration
* Supports all base_serp features

Requirements:
-------------
* base_serp module installed
* SerpAPI account and API key (get from https://serpapi.com)
* google-search-results Python package

Usage:
------
1. Install this module
2. Get API key from https://serpapi.com
3. Go to SERP → Configuration → Providers
4. Create or edit SerpAPI provider
5. Enter your API key
6. Use it on partners for tracking
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'license': 'AGPL-3',
    'depends': [
        'base_serp',
    ],
    'external_dependencies': {
        'python': [
            'google-search-results',
        ],
    },
    'data': [
        'data/serp_provider_data.xml',
        'views/serp_provider_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}