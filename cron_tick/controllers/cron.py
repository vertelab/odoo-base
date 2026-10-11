# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

"""Händelsedriven triggning av cron.task.

Samma mönster som `/saltstack/log` och `/saltstack/alert`:

    1. Enabled?          (ir.config_parameter)
    2. Bearer token      (hmac.compare_digest)
    3. Alltid HTTP 200   (senders ska inte retry:a i oändlighet)

Anropas av Salt efter deploy, eller av vilken händelsekälla som helst som
vill köra en uppgift omedelbart i stället för att vänta på nästa tick.
"""

import hmac
import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class CronTriggerController(http.Controller):

    @http.route('/cron/trigger/<string:technical_name>', type='json',
                auth='none', methods=['POST'], csrf=False)
    def cron_trigger(self, technical_name, **kwargs):
        """Kör en uppgift omedelbart via webhook.

        Alltid HTTP 200 — en avsändare som får 4xx/5xx retry:ar i oändlighet,
        och triggningen är inte idempotent i sig (uppgiften körs).
        """
        params = request.env['ir.config_parameter'].sudo()

        # 1. Enabled?
        if params.get_param('cron_tick.webhook_enabled', 'True') not in (
                'True', 'true', '1'):
            return {'status': 'disabled'}

        # 2. Bearer token — egen nyckel prioriteras, annars saltstack-nyckeln
        #    så att Salt-minions inte behöver en andra nyckel.
        expected = params.get_param('cron_tick.webhook_token', '')
        if not expected:
            expected = params.get_param('saltstack.alert.webhook_token', '')
        auth_header = request.httprequest.headers.get('Authorization', '')
        provided = auth_header[7:] if auth_header.startswith('Bearer ') else ''
        if not expected or not hmac.compare_digest(provided, expected):
            _logger.warning(
                'cron.trigger: ogiltig/saknad Bearer token (len=%s) för %s',
                len(provided), technical_name)
            return {'status': 'error', 'error': 'Unauthorized'}

        # 3. Slå upp uppgiften
        task = request.env['cron.task'].sudo()._find_by_technical_name(
            technical_name)
        if not task:
            _logger.info('cron.trigger: okänt tekniskt namn %s', technical_name)
            return {'status': 'not_found', 'technical_name': technical_name}

        # 4. Kör — samma väg som tick och manuell körning.
        try:
            result = task._execute(owner='webhook')
        except Exception as exc:  # noqa: BLE001 — alltid 200
            _logger.exception(
                'cron.trigger: %s kastade', technical_name)
            return {'status': 'error', 'error': str(exc)}

        _logger.info(
            'cron.trigger: %s → %s (%s ms)',
            technical_name, result.get('status'), result.get('duration_ms'))
        return result
