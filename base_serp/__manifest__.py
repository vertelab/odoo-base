# -*- coding: utf-8 -*-
{
    'name': 'Base: SERP Tracker',
    'version': '18.0.1.3.0',
    'category': 'Marketing',
    'summary': 'Track Search Engine Results Page (SERP) positions for domains and keywords.',
    'description': '''
Base SERP Tracker
=================

    Track SERP (Search Engine Results Page) positions for multiple companies/domains across various keywords.

    Features:
    * Track unlimited domains and keywords
    * Multiple search engines support (Google by default)
    * Provider-based architecture (BeautifulSoup default, extensible)
    * Historical ranking data storage
    * Scheduled tracking via cron jobs
    * Multi-language support (Swedish, English)
    * Graph-based reporting and analytics

    Provider System:
    * Pluggable provider architecture
    * Default: BeautifulSoup (web scraping)
    * Easily extend with additional providers (SerpAPI, etc.)

    Features:

        - Automation: Scheduled jobs: SERP: Run SERP Check on Partners, SERP Report: Generate SERP Report.
        - Guided Wizards: Step-by-step dialogs for data entry.
        - Reports: Adds printable reports.
        - UI Integration: Extends 10 view(s) in the Odoo interface.
        - Extends Odoo: Builds on project.task, serp.keyword, serp.mixin, serp.provider.
    ''',
    'author': 'Vertel Sverige AB',
    'website': 'https://vertel.se/apps/odoo-base/base_serp',
    'license': 'AGPL-3',
    'depends': [
        'base_setup',
        'web',
        'website',
    ],
    'external_dependencies': {
        'python': [
            'requests',
            'beautifulsoup4',
            'fake_useragent',
        ],
    },
    'data': [
        'security/serp_security.xml',
        'security/ir.model.access.csv',

        'report/ir_actions_report.xml',
        'report/ir_actions_report_templates.xml',

        'data/serp_provider_data.xml',
        'data/serp_cron.xml',
        'data/serp_actions.xml',
        'data/mail_templates.xml',

        'views/serp_provider_views.xml',
        'views/serp_result_views.xml',
        'views/res_partner_views.xml',
        'views/res_config_views.xml',
        'views/project_task_views.xml',
        'views/website_analytics_provider_views.xml',
        'views/website_analytics_report_type_views.xml',
        'views/ir_ui_view.xml',
        'views/templates.xml',

        'wizards/website_analytics_report_type_preview_views.xml',



        'views/menus.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}