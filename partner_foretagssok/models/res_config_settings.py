# -*- coding: utf-8 -*-
import logging
import os

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = 'https://data.foretagsapi.se'


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    foretagssok_api_key = fields.Char(
        string='FöretagsAPI API Key',
        config_parameter='partner_foretagssok.api_key',
    )
    foretagssok_base_url = fields.Char(
        string='FöretagsAPI Base URL',
        config_parameter='partner_foretagssok.base_url',
        default=DEFAULT_BASE_URL,
    )

    @api.model
    def load_env_api_key(self):
        """Load API key from .env file if the system parameter is empty."""
        params = self.env['ir.config_parameter'].sudo()
        current = params.get_param('partner_foretagssok.api_key', default='').strip()
        if current:
            return

        env_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            '.env',
        )
        if not os.path.exists(env_path):
            _logger.info('No .env file found at %s', env_path)
            return

        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    if '=' not in line:
                        continue
                    key, value = line.split('=', 1)
                    if key.strip() == 'FORETAGSSOK_API_KEY':
                        value = value.strip().strip('"').strip("'")
                        if value:
                            params.set_param('partner_foretagssok.api_key', value)
                            _logger.info('FöretagsAPI API key loaded from .env')
                        break
        except Exception as e:
            _logger.warning('Could not read FöretagsAPI .env file: %s', e)
