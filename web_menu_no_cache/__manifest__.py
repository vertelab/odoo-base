# -*- coding: utf-8 -*-
# Copyright 2026 Vertel AB — License AGPL-3.0
{
    'name': 'Base: Web Menu No Cache',
    'version': '18.0.1.0.0',
    'category': 'Technical',
    'summary': 'Send no-cache for /web/webclient/load_menus so menu updates always reach clients.',
    'description': '''
Web Menu No Cache
=================

    Prevents browsers from caching the Odoo menu tree (load_menus). Without this,
    after module upgrades that add/remove apps, users see a stale menu until they
    manually clear the browser cache.

    Features:

        - Web integration: Exposes HTTP endpoints for external systems.
    ''',
    'author': 'Vertel AB',
    'website': 'https://vertel.se/apps/odoo-base/web_menu_no_cache',
    'license': 'AGPL-3',
    'depends': ['web'],
    'data': [],
    'installable': True,
    'application': False,
}
