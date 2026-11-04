# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

"""cron.task.log — one record per run.

WHY A DEDICATED MODEL
    `cron.task` keeps only the LATEST run (`last_run`, `last_duration_ms`,
    `failure_count`, `last_error`). The history is gone: you cannot see that a
    task started failing two days ago, that a task is slow on Tuesdays, or
    that a webhook ran it. `last_error` is overwritten by the next successful
    run — the error survives only until the task happens to succeed again.

    `mail.message` is not a substitute: machine-written history at this volume
    (the `min` tick can produce thousands of rows a day) cannot be filtered on
    status, aggregated per task, or pruned per task.

ONE WRITE POINT
    The engine writes the log in `_record_success()`/`_record_failure()` —
    never in `_run()`. If `_run()` wrote the log and then raised, the savepoint
    would roll back the write and the log would disappear exactly when it is
    needed most.

    The log write is wrapped in try/except by the engine: history must never
    be the reason a run is reported as failed.

STATUS → COLOUR
    ok      green/neutral
    error   red      (decoration-danger)
    locked  orange   (decoration-warning)
    skipped muted    (decoration-muted)
"""

import logging
from datetime import timedelta

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)

# Fallback when the system parameter is missing or unparsable.
DEFAULT_RETENTION_DAYS = 90

# Delete in batches so the first cleanup on a large table does not run as one
# giant transaction.
CLEANUP_BATCH_SIZE = 5000


class CronTaskLog(models.Model):
    _name = 'cron.task.log'
    _description = 'Scheduled Task Run Log'
    _order = 'run_at desc, id desc'
    _rec_name = 'display_name'

    # ── What ran ───────────────────────────────────────────────────────
    task_id = fields.Many2one(
        'cron.task', required=True, index=True, ondelete='cascade',
        string='Task')
    # Snapshot of the identity, so the log stays readable after the task is
    # renamed (or if the task row is removed by a module uninstall — the
    # cascade removes the log with it, but the name is still useful in the
    # window before that happens).
    task_name = fields.Char(string='Task Name')
    technical_name = fields.Char(index=True)
    module = fields.Char(index=True)

    # ── When / how ─────────────────────────────────────────────────────
    run_at = fields.Datetime(
        required=True, index=True, default=fields.Datetime.now,
        help='When the run started.')
    status = fields.Selection([
        ('ok', 'OK'),
        ('error', 'Error'),
        ('locked', 'Locked'),
        ('skipped', 'Skipped'),
    ], required=True, index=True, default='ok',
        help='ok = the method returned without error.\n'
             'error = the method raised; see the text.\n'
             'locked = another session was running the task; the method was '
             'not called.\n'
             'skipped = the engine decided not to run it (nothing to clean '
             'up, task inactive).')
    trigger = fields.Selection([
        ('tick', 'Scheduled'),
        ('webhook', 'Webhook'),
        ('manual', 'Manual'),
    ], required=True, default='tick', index=True,
        help='Which of the three run paths started the run.')
    trigger_detail = fields.Char(
        help='The cadence for a tick run ("daily"), or the user for a manual '
             'run.')
    user_id = fields.Many2one(
        'res.users', string='Run by',
        help='Set for manual runs — who pressed "Run now".')

    # ── Result ─────────────────────────────────────────────────────────
    duration_ms = fields.Integer(
        help='Measured run time. 0 for locked/skipped runs.')
    text = fields.Text(
        help='Short description of what happened. The error message for a '
             'failed run.')

    display_name = fields.Char(compute='_compute_display_name')

    # ───────────────────────────────────────────────────────────────────
    # Computed
    # ───────────────────────────────────────────────────────────────────

    @api.depends('task_name', 'technical_name', 'run_at', 'status')
    def _compute_display_name(self):
        for log in self:
            name = log.task_name or log.technical_name or _('Unknown task')
            log.display_name = '%s — %s (%s)' % (
                log.run_at or '', name, log.status or '')

    # ───────────────────────────────────────────────────────────────────
    # Factory — the ONLY way the engine creates a log record
    # ───────────────────────────────────────────────────────────────────

    @api.model
    def _log_run(self, task, status, trigger, trigger_detail=None,
                 duration_ms=0, text=None, user_id=None):
        """Create one log record for one run.

        Called by the engine after the run finished (or was refused). Never
        raises: a broken log write must not turn a successful run into a
        failure, nor hide the original error.

        `task` is a `cron.task` recordset (browse'd after `invalidate_all()`
        when the caller came back from a rolled-back savepoint).
        """
        try:
            with self.env.cr.savepoint():
                return self.sudo().create({
                    'task_id': task.id,
                    'task_name': task.name,
                    'technical_name': task.technical_name,
                    'module': task.module,
                    'run_at': fields.Datetime.now(),
                    'status': status,
                    'trigger': trigger,
                    'trigger_detail': trigger_detail,
                    'user_id': user_id or False,
                    'duration_ms': duration_ms or 0,
                    'text': text,
                })
        except Exception:  # noqa: BLE001 — history must never break a run
            _logger.exception(
                'cron.task.log: could not record a %s run of %s',
                status, task.technical_name if task else '?')
            return self.browse()

    # ───────────────────────────────────────────────────────────────────
    # Retention
    # ───────────────────────────────────────────────────────────────────

    @api.model
    def _retention_days(self):
        """Read `cron_tick.log_retention_days` (default 90).

        A value of 0 or less disables cleanup entirely — that is the
        documented rollback switch.
        """
        raw = self.env['ir.config_parameter'].sudo().get_param(
            'cron_tick.log_retention_days', DEFAULT_RETENTION_DAYS)
        try:
            days = int(raw)
        except (TypeError, ValueError):
            _logger.warning(
                'cron.task.log: invalid cron_tick.log_retention_days=%r — '
                'using %s', raw, DEFAULT_RETENTION_DAYS)
            days = DEFAULT_RETENTION_DAYS
        return days

    @api.model
    def _cron_cleanup(self):
        """Delete log records older than the retention window.

        Registered as a `cron.task` (`cron_log_cleanup`, daily cadence) so it
        is visible and manually runnable like every other task. Deletes in
        batches to avoid one huge transaction on the first run.
        """
        days = self._retention_days()
        if days <= 0:
            _logger.info(
                'cron.task.log: retention disabled (log_retention_days=%s)',
                days)
            return {'deleted': 0, 'days': days, 'disabled': True}

        limit = fields.Datetime.now() - timedelta(days=days)
        total = 0
        while True:
            old = self.sudo().search(
                [('run_at', '<', limit)], order='id', limit=CLEANUP_BATCH_SIZE)
            if not old:
                break
            count = len(old)
            old.unlink()
            total += count
            # Flush per batch so the next search sees the deletion.
            self.env.flush_all()
            if count < CLEANUP_BATCH_SIZE:
                break

        _logger.info(
            'cron.task.log: deleted %s records older than %s days',
            total, days)
        return {'deleted': total, 'days': days}
