# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

"""Event-driven triggering of cron.task.

The same pattern as `/saltstack/log` and `/saltstack/alert`:

    1. Enabled?          (ir.config_parameter)
    2. Bearer token      (hmac.compare_digest)
    3. Always HTTP 200   (senders should not retry forever)

Called by Salt after deploy, or by any event source that wants to run a
task immediately instead of waiting for the next tick.
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
        """Run a task immediately via webhook.

        Always HTTP 200 — a sender that receives 4xx/5xx retries forever,
        and the trigger is not idempotent in itself (the task runs).
        """
        params = request.env['ir.config_parameter'].sudo()

        # 1. Enabled?
        if params.get_param('cron_tick.webhook_enabled', 'True') not in (
                'True', 'true', '1'):
            return {'status': 'disabled'}

        # 2. Bearer token — our own key takes precedence, otherwise the
        #    saltstack key, so Salt minions do not need a second key.
        expected = params.get_param('cron_tick.webhook_token', '')
        if not expected:
            expected = params.get_param('saltstack.alert.webhook_token', '')
        auth_header = request.httprequest.headers.get('Authorization', '')
        provided = auth_header[7:] if auth_header.startswith('Bearer ') else ''
        if not expected or not hmac.compare_digest(provided, expected):
            _logger.warning(
                'cron.trigger: invalid/missing Bearer token (len=%s) for %s',
                len(provided), technical_name)
            return {'status': 'error', 'error': 'Unauthorized'}

        # 3. Look up the task
        task = request.env['cron.task'].sudo()._find_by_technical_name(
            technical_name)
        if not task:
            _logger.info('cron.trigger: unknown technical name %s',
                         technical_name)
            return {'status': 'not_found', 'technical_name': technical_name}

        # 4. Run — the same path as tick and manual execution.
        try:
            result = task._execute(owner='webhook')
        except Exception as exc:  # noqa: BLE001 — always 200
            _logger.exception('cron.trigger: %s raised', technical_name)
            return {'status': 'error', 'error': str(exc)}

        _logger.info(
            'cron.trigger: %s -> %s (%s ms)',
            technical_name, result.get('status'), result.get('duration_ms'))
        return result
