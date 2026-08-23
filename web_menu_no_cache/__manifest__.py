# -*- coding: utf-8 -*-
# Copyright 2026 Vertel AB — License AGPL-3.0
{
    'name': 'Web Menu No Cache',
    'version': '18.0.1.0.0',
    'category': 'Technical',
    'summary': 'Send no-cache for /web/webclient/load_menus so menu updates always reach clients',
    'description': """
Prevents browsers from caching the Odoo menu tree (load_menus). Without this,
after module upgrades that add/remove apps, users see a stale menu until they
manually clear the browser cache.
    """,
    'author': 'Vertel AB',
    'license': 'AGPL-3',
    'depends': ['web'],
    'data': [],
    'installable': True,
    'application': False,
}
