# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = 'https://data.foretagsapi.se'


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # The API key is deliberately NOT a settings field.
    #
    # It used to be a ``fields.Char(config_parameter=...)``, which meant the
    # credential lived in ``ir.config_parameter``: readable by every user who
    # can open settings, present in every database dump, and impossible to
    # rotate without a database write. It now lives in keykeep (purpose
    # ``foretagssok``) and is pushed to ``/etc/odoo/enrich.env`` by
    # maintenance-runner. Only the non-secret base URL stays here.
    foretagssok_base_url = fields.Char(
        string='FöretagsAPI Base URL',
        config_parameter='partner_foretagssok.base_url',
        default=DEFAULT_BASE_URL,
    )

    foretagssok_api_key_state = fields.Char(
        string='FöretagsAPI Key',
        compute='_compute_foretagssok_api_key_state',
        help='Where the API key was found, if anywhere. Set it in keykeep.',
    )

    @api.depends('foretagssok_base_url')
    def _compute_foretagssok_api_key_state(self):
        partner_model = self.env['res.partner']
        for settings in self:
            key = partner_model._foretagsapi_secret_from_keykeep()
            if key:
                settings.foretagssok_api_key_state = _('Configured (keykeep)')
                continue
            if partner_model._foretagsapi_secret_from_env():
                settings.foretagssok_api_key_state = _(
                    'Configured (environment file)'
                )
                continue
            settings.foretagssok_api_key_state = _('Not configured')
