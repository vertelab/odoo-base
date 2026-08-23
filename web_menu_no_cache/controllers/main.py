# -*- coding: utf-8 -*-
# Copyright 2026 Vertel AB — License AGPL-3.0
from odoo import http
from odoo.addons.web.controllers.home import Home


class WebMenuNoCacheHome(Home):
    """Sätt no-cache på /web/webclient/load_menus.

    Odoo:s default svarar med Cache-Control: public, max-age=<lång>, vilket gör
    att webbläsare serverar en gammal menystruktur utan att fråga servern —
    appar (t.ex. Keykeep/Bifrost/Saltstack) försvinner efter moduluppdateringar
    tills cachen rensas manuellt. Den här overriden tvingar alltid färskt svar.
    """

    @http.route(
        "/web/webclient/load_menus/<string:unique>",
        type="http",
        auth="user",
        methods=["GET"],
        readonly=True,
    )
    def web_load_menus(self, unique, lang=None):
        response = super().web_load_menus(unique, lang=lang)
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        return response
