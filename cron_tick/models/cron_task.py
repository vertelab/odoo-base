# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

"""cron.task — declarative scheduling.

One record per scheduled task. Modules declare their tasks as data XML;
this module owns the engine. The engine knows nothing about any task.

CADENCE, NOT INTERVAL
    A task states *which* cadence it belongs to (min/hour/daily/week/month),
    not an interval in seconds. That removes the per-task `next_run`
    arithmetic and the entire class of calculation errors (wrong timedelta,
    wrong timezone, forgotten next_run on failure). Only the tick needs to
    know when to run.

THE ENGINE OWNS THE RUN HISTORY
    `_run()` NEVER touches `last_run`/`failure_count`. The engine writes
    those after the task returned or raised — one write point, not two.
    If `_run()` set `last_run` and then raised, the savepoint would roll
    back the write and the engine would believe the task never ran.
"""

import hashlib
import logging
import time
from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

# Cadence → approximate number of seconds. Used only for overdue detection
# and logging — NOT for scheduling (the tick cron owns that).
CADENCE_SECONDS = {
    'min': 300,
    'hour': 3600,
    'daily': 86400,
    'week': 604800,
    'month': 2592000,
}

# Spread window per cadence (minutes). A `daily` task spreads over an hour,
# a `week` task over a day, a `month` task over a week. Without spreading,
# 19 daily jobs would all run at 00:00 and create a spike of heavy batch
# operations at the same moment.
SPREAD_MINUTES = {
    'min': 0,
    'hour': 0,
    'daily': 60,
    'week': 1440,
    'month': 10080,
}

# Interval type → number of seconds. Used by tasks that set
# `interval_number`/`interval_type` instead of a cadence. Approximate for
# months (30 days), which is the same convention as CADENCE_SECONDS.
INTERVAL_SECONDS = {
    'minutes': 60,
    'hours': 3600,
    'days': 86400,
    'weeks': 604800,
    'months': 2592000,
}

# The cadence the interval tick runs under. Interval tasks are checked by a
# tick cron of this cadence; the task itself is due when its own interval has
# elapsed. 5 minutes matches ir.cron's granularity.
INTERVAL_TICK_CADENCE = 'min'


class CronTask(models.Model):
    _name = 'cron.task'
    _description = 'Scheduled Task'
    _order = 'sequence, id'

    # ── Identity ───────────────────────────────────────────────────────
    name = fields.Char(
        required=True,
        help='Readable name shown in the list.')
    technical_name = fields.Char(
        required=True, index=True,
        help='Stable identifier. Used by event-driven triggering '
             '(/cron/trigger/<technical_name>) and for daily spread. '
             'Never change it on a task already in production.')
    module = fields.Char(
        index=True,
        help='The module that owns the task. On uninstall the XML record is '
             'removed and the task disappears.')

    # ── What to run ────────────────────────────────────────────────────
    model_name = fields.Char(
        required=True,
        help='Technical model name, e.g. "ai.skill". Resolved at run time — '
             'therefore robust against modules being uninstalled.')
    method_name = fields.Char(
        required=True,
        help='Method name on the model, e.g. "_sync_from_filesystem". '
             'Called without arguments.')

    # ── When ───────────────────────────────────────────────────────────
    cadence = fields.Selection([
        ('min', 'Every 5 minutes'),
        ('hour', 'Hourly'),
        ('daily', 'Daily'),
        ('week', 'Weekly'),
        ('month', 'Monthly'),
    ], index=True,
        help='Which tick cron runs the task. The cadence is a FIELD — a name '
             'prefix in the technical name does not affect execution.\n\n'
             'Leave empty when `interval_number`/`interval_type` are set: a '
             'task uses EITHER a cadence OR an interval, never both.')
    interval_number = fields.Integer(
        help='Run every N `interval_type` units, measured from the last run. '
             'Use this instead of `cadence` when the task needs an interval '
             'the five cadences cannot express (15 minutes, 6 hours, 14 days).\n\n'
             'The task is checked by the "interval" tick every 5 minutes, so '
             'the effective granularity is 5 minutes — the same as ir.cron.')
    interval_type = fields.Selection([
        ('minutes', 'Minutes'),
        ('hours', 'Hours'),
        ('days', 'Days'),
        ('weeks', 'Weeks'),
        ('months', 'Months'),
    ], help='Unit for `interval_number`.')
    sequence = fields.Integer(
        default=10,
        help='Run order within the cadence. Lower value runs first.')
    active = fields.Boolean(default=True)

    # ── Execution ──────────────────────────────────────────────────────
    timeout_seconds = fields.Integer(
        default=120,
        help='Soft time limit. The engine measures the run time and logs a '
             'warning when the limit is exceeded. Python threads cannot be '
             'aborted safely — the limit is therefore measuring, not '
             'aborting. A task that consistently exceeds the limit should be '
             'moved to queue_job.')
    max_failures = fields.Integer(
        default=10,
        help='Number of consecutive failures before the task is '
             'automatically deactivated.')

    # ── Run history (owned by the engine) ──────────────────────────────
    last_run = fields.Datetime(readonly=True)
    last_duration_ms = fields.Integer(readonly=True)
    failure_count = fields.Integer(readonly=True, default=0)
    last_error = fields.Text(readonly=True)

    # ── Lock (atomic, D10) ─────────────────────────────────────────────
    locked_by = fields.Char(
        readonly=True,
        help='Who is running the task right now (e.g. "tick:min" or '
             '"webhook"). Empty = free.')
    locked_at = fields.Datetime(readonly=True)

    # ── Computed fields ────────────────────────────────────────────────
    is_locked = fields.Boolean(
        compute='_compute_is_locked', search='_search_is_locked')
    is_overdue = fields.Boolean(
        compute='_compute_is_overdue', search='_search_is_overdue',
        help='True when the task has not run within three cadence intervals.')
    cadence_label = fields.Char(
        compute='_compute_cadence_label')

    _sql_constraints = [
        ('technical_name_uniq', 'UNIQUE(technical_name)',
         'The technical name must be unique — it is the identity of the task.'),
    ]

    # ───────────────────────────────────────────────────────────────────
    # Computed fields
    # ───────────────────────────────────────────────────────────────────

    @api.depends('locked_by')
    def _compute_is_locked(self):
        for task in self:
            task.is_locked = bool(task.locked_by)

    @api.depends('last_run', 'cadence', 'active')
    def _compute_is_overdue(self):
        now = fields.Datetime.now()
        for task in self:
            if not task.active or not task.last_run:
                task.is_overdue = False
                continue
            limit = CADENCE_SECONDS.get(task.cadence, 86400) * 3
            task.is_overdue = (now - task.last_run).total_seconds() > limit

    @api.depends('cadence')
    def _compute_cadence_label(self):
        labels = dict(self._fields['cadence'].selection)
        for task in self:
            task.cadence_label = labels.get(task.cadence, task.cadence or '')

    def _search_is_locked(self, operator, value):
        """Searchable counterpart of `is_locked` (locked_by is set)."""
        if operator in ('=', '!=') and isinstance(value, bool):
            # is_locked = True  → locked_by != False
            # is_locked = False → locked_by = False
            if (operator == '=' and value) or (operator == '!=' and not value):
                return [('locked_by', '!=', False)]
            return [('locked_by', '=', False)]
        return [('locked_by', operator, value)]

    def _search_is_overdue(self, operator, value):
        """Searchable counterpart of `is_overdue`.

        Overdue = active, has run, and the last run is older than three
        cadence intervals. The threshold depends on the cadence, so we build
        an OR across the cadences.

        WARNING: Odoo 18 wants a FLAT domain in prefix notation — nested
        lists crash in `domain_combine_anies`.

        WARNING: prefix notation requires one operator TOKEN per join:
        a group of 3 operands needs '&','&' (not a single '&' — then the
        operator binds incorrectly and the domain matches nothing).
        The same applies to the OR chain: N branches require N-1 leading '|'.
        """
        now = fields.Datetime.now()
        if operator not in ('=', '!='):
            return []
        want = value if operator == '=' else not value

        # One OR branch per cadence: (cadence = X AND last_run < threshold)
        branches = []
        for cadence, seconds in CADENCE_SECONDS.items():
            limit = now - timedelta(seconds=seconds * 3)
            branches.append([
                ('cadence', '=', cadence),
                ('last_run', '!=', False),
                ('last_run', '<', limit),
            ])

        def _and_group(branch):
            return ['&'] * (len(branch) - 1) + list(branch)

        if want:
            or_ops = ['|'] * (len(branches) - 1)
            return or_ops + [t for b in branches for t in _and_group(b)]

        # NOT(OR over branches) — negate each branch separately and AND them.
        # NOT(a OR b) == (NOT a) AND (NOT b)
        negated = [['!'] + _and_group(b) for b in branches]
        and_ops = ['&'] * (len(negated) - 1)
        return and_ops + [t for g in negated for t in g]

    # ───────────────────────────────────────────────────────────────────
    # Spread (D7)
    # ───────────────────────────────────────────────────────────────────

    def _spread_offset_minutes(self):
        """Deterministic spread within the cadence window.

        The same technical name yields the same offset every time — a
        `daily` task therefore runs at the same time every day, not randomly.
        """
        self.ensure_one()
        window = SPREAD_MINUTES.get(self.cadence, 0)
        if not window:
            return 0
        digest = hashlib.sha256(
            (self.technical_name or '').encode('utf-8')).hexdigest()
        return int(digest, 16) % window

    # ───────────────────────────────────────────────────────────────────
    # Cadence logic (D7)
    # ───────────────────────────────────────────────────────────────────

    def _is_due(self, now=None):
        """Is the task due in its cadence?

        `min`/`hour` are governed by the time elapsed since the last run.
        `daily`/`week`/`month` are governed by the spread window — the task
        runs when the window has opened and it has not already run in the
        period.
        """
        self.ensure_one()
        now = now or fields.Datetime.now()

        if self.cadence == 'min':
            return True

        if self.cadence == 'hour':
            if not self.last_run:
                return True
            return (now - self.last_run).total_seconds() >= 3600

        # daily / week / month — spread over a window.
        offset = self._spread_offset_minutes()
        if self.cadence == 'daily':
            # The window is one hour: run when minute >= offset and not run today.
            if not self.last_run:
                return now.minute >= offset
            return self.last_run.date() < now.date() and now.minute >= offset

        if self.cadence == 'week':
            # The window is one day (1440 min): offset in minutes since midnight.
            window_open = now.hour * 60 + now.minute >= offset
            if not self.last_run:
                return window_open
            return (now - self.last_run).days >= 7 and window_open

        if self.cadence == 'month':
            # The window is one week (10080 min): offset in minutes since
            # the start of the week (Monday 00:00).
            minutes_into_week = now.weekday() * 1440 + now.hour * 60 + now.minute
            window_open = minutes_into_week >= offset
            if not self.last_run:
                return window_open
            return (now - self.last_run).days >= 28 and window_open

        return False

    # ───────────────────────────────────────────────────────────────────
    # Execution — the single run path (D9, D12)
    # ───────────────────────────────────────────────────────────────────

    def _run(self):
        """Run the task. A PURE method — never touches the run history.

        Returns the method's result. Propagates errors to the caller, which
        records them. The engine (and webhook/manual) owns `last_run`,
        `last_duration_ms` and `failure_count`.
        """
        self.ensure_one()
        model = self.env.get(self.model_name)
        if model is None:
            raise UserError(_(
                'The model "%s" does not exist (task %s). The module may be '
                'uninstalled.') % (self.model_name, self.technical_name))
        method = getattr(model, self.method_name, None)
        if method is None or not callable(method):
            raise UserError(_(
                'The method "%s" does not exist on the model "%s" (task %s).'
            ) % (self.method_name, self.model_name, self.technical_name))
        return method()

    def _execute(self, owner='manual'):
        """Run the task with locking, measuring and recording.

        This is the common path for all three trigger types. Returns a dict
        with status and duration.
        """
        self.ensure_one()
        if not self._acquire_lock(owner):
            return {
                'status': 'locked',
                'technical_name': self.technical_name,
            }
        started = time.monotonic()
        try:
            try:
                with self.env.cr.savepoint():
                    self._run()
            except Exception as exc:  # noqa: BLE001 — the engine catches all
                duration_ms = int((time.monotonic() - started) * 1000)
                self.env.invalidate_all()
                self.browse(self.id)._record_failure(exc, duration_ms)
                _logger.exception(
                    'cron.task %s failed (%s ms)',
                    self.technical_name, duration_ms)
                return {
                    'status': 'error',
                    'technical_name': self.technical_name,
                    'duration_ms': duration_ms,
                    'error': str(exc),
                }
            duration_ms = int((time.monotonic() - started) * 1000)
            self.env.invalidate_all()
            task = self.browse(self.id)
            task._record_success(duration_ms)
            if duration_ms > self.timeout_seconds * 1000:
                _logger.warning(
                    'cron.task %s exceeded the time limit: %s ms > %s s',
                    self.technical_name, duration_ms, self.timeout_seconds)
            return {
                'status': 'ok',
                'technical_name': self.technical_name,
                'duration_ms': duration_ms,
            }
        finally:
            # Release the advisory lock EVEN on error — otherwise it is held
            # until the connection closes and the task can never run again.
            self.browse(self.id)._release_lock()

    # ───────────────────────────────────────────────────────────────────
    # Lock (D10 — atomic via advisory lock, independent of isolation level)
    # ───────────────────────────────────────────────────────────────────

    def _acquire_lock(self, owner):
        """Acquire the lock atomically. Returns True if we got it.

        WARNING: a conditional UPDATE is NOT sufficient: Odoo runs under
        `repeatable read`, and two transactions can both see `locked_by` as
        empty in their snapshot and both get `rowcount == 1`. Verified in
        production — two concurrent workers ran the same task.

        We use a session-bound advisory lock per task
        (`pg_try_advisory_lock`), which is atomic regardless of isolation
        level. `locked_by`/`locked_at` are written as INFORMATION (who is
        running), not as the lock itself — the latter is owned by PostgreSQL.

        The lock is released by `_release_lock()` or automatically when the
        session (connection) closes.
        """
        self.ensure_one()
        lock_id = self._task_lock_id()
        self.env.cr.execute('SELECT pg_try_advisory_lock(%s)', (lock_id,))
        row = self.env.cr.fetchone()
        if not row or not row[0]:
            return False
        # We own the lock. Write information about who is running.
        self.env.cr.execute("""
            UPDATE cron_task
               SET locked_by = %s, locked_at = now()
             WHERE id = %s
        """, (owner, self.id))
        self.env.invalidate_all()
        return True

    def _release_lock(self):
        """Release the lock after the run."""
        self.ensure_one()
        lock_id = self._task_lock_id()
        self.env.cr.execute('SELECT pg_advisory_unlock(%s)', (lock_id,))
        self.env.cr.execute("""
            UPDATE cron_task
               SET locked_by = NULL, locked_at = NULL
             WHERE id = %s
        """, (self.id,))
        self.env.invalidate_all()

    def _task_lock_id(self):
        """Stable advisory lock id per task (fits in int8).

        A dedicated namespace prefix keeps task locks separate from the
        cadence locks in `_advisory_lock_id`.
        """
        self.ensure_one()
        digest = hashlib.sha256(
            ('cron_task:lock:%s' % self.technical_name).encode('utf-8')
        ).hexdigest()
        return int(digest, 16) % (2 ** 31)

    # ───────────────────────────────────────────────────────────────────
    # Recording (D8, D9)
    # ───────────────────────────────────────────────────────────────────

    def _record_success(self, duration_ms):
        """Record a successful run. Resets the failure counter."""
        self.ensure_one()
        self.write({
            'last_run': fields.Datetime.now(),
            'last_duration_ms': duration_ms,
            'failure_count': 0,
            'last_error': False,
            'locked_by': False,
            'locked_at': False,
        })

    def _record_failure(self, exc, duration_ms=0):
        """Record a failed run. Deactivates after `max_failures`.

        WARNING: called AFTER the savepoint has been rolled back — the caller
        must have run `invalidate_all()` and re-fetched the record, otherwise
        we write to a record whose transaction is gone.
        """
        self.ensure_one()
        count = self.failure_count + 1
        vals = {
            'last_run': fields.Datetime.now(),
            'last_duration_ms': duration_ms,
            'failure_count': count,
            'last_error': str(exc)[:4000],
            'locked_by': False,
            'locked_at': False,
        }
        if count >= self.max_failures:
            vals['active'] = False
            _logger.error(
                'cron.task %s deactivated after %s consecutive failures',
                self.technical_name, count)
        self.write(vals)

    # ───────────────────────────────────────────────────────────────────
    # The engine (D6, D8, D11)
    # ───────────────────────────────────────────────────────────────────

    @api.model
    def _cron_tick(self, cadence):
        """Run all due tasks in one cadence.

        Protected by a global advisory lock per cadence (D11) so that two
        Odoo workers do not run the same cadence simultaneously.
        """
        lock_id = self._advisory_lock_id(cadence)
        self.env.cr.execute('SELECT pg_try_advisory_lock(%s)', (lock_id,))
        got_lock = self.env.cr.fetchone()
        if not got_lock or not got_lock[0]:
            _logger.info(
                'cron.tick %s: another worker is already running — skipping',
                cadence)
            return {'cadence': cadence, 'skipped': 'locked'}

        try:
            now = fields.Datetime.now()
            candidates = self.search([
                ('active', '=', True),
                ('cadence', '=', cadence),
            ], order='sequence, id')
            due = candidates.filtered(lambda t: t._is_due(now))

            ran, failed, locked = 0, 0, 0
            for task in due:
                task_id = task.id
                if not task._acquire_lock('tick:%s' % cadence):
                    locked += 1
                    continue
                started = time.monotonic()
                try:
                    try:
                        with self.env.cr.savepoint():
                            task._run()
                    except Exception as exc:  # noqa: BLE001
                        duration_ms = int((time.monotonic() - started) * 1000)
                        # The savepoint was rolled back — the ORM cache is
                        # corrupt. Re-fetch the record before writing the
                        # error (D8).
                        self.env.invalidate_all()
                        self.browse(task_id)._record_failure(exc, duration_ms)
                        _logger.exception(
                            'cron.task %s failed in tick %s',
                            task.technical_name, cadence)
                        failed += 1
                        continue
                    duration_ms = int((time.monotonic() - started) * 1000)
                    self.env.invalidate_all()
                    self.browse(task_id)._record_success(duration_ms)
                    if duration_ms > task.timeout_seconds * 1000:
                        _logger.warning(
                            'cron.task %s exceeded the time limit: %s ms > %s s',
                            task.technical_name, duration_ms,
                            task.timeout_seconds)
                    ran += 1
                finally:
                    # Release the task lock every iteration — otherwise it is
                    # held until the connection closes and the task is blocked.
                    self.browse(task_id)._release_lock()

            _logger.info(
                'cron.tick %s: %s ran, %s failed, %s locked',
                cadence, ran, failed, locked)
            return {
                'cadence': cadence,
                'ran': ran,
                'failed': failed,
                'locked': locked,
            }
        finally:
            self.env.cr.execute(
                'SELECT pg_advisory_unlock(%s)', (lock_id,))

    @api.model
    def _advisory_lock_id(self, cadence):
        """Stable advisory lock id per cadence (fits in int4)."""
        digest = hashlib.sha256(
            ('cron_tick:%s' % cadence).encode('utf-8')).hexdigest()
        return int(digest, 16) % (2 ** 31)

    # ───────────────────────────────────────────────────────────────────
    # Manual run (D12)
    # ───────────────────────────────────────────────────────────────────

    def action_run_now(self):
        """Run the task immediately — manual trigger.

        Respects the lock: a task already running is refused with a clear
        message instead of being run twice.
        """
        self.ensure_one()
        result = self._execute(owner='manual')
        if result['status'] == 'locked':
            raise UserError(_(
                'The task "%s" is already running (%s). Try again when it '
                'has finished.') % (self.name, self.locked_by or 'unknown'))
        if result['status'] == 'error':
            raise UserError(_(
                'The task "%s" failed:\n%s'
            ) % (self.name, result.get('error', '')))
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Task executed'),
                'message': _(
                    '%s ran in %s ms.') % (
                    self.name, result.get('duration_ms', 0)),
                'type': 'success',
                'sticky': False,
            },
        }

    # ───────────────────────────────────────────────────────────────────
    # Helpers for the webhook (D12)
    # ───────────────────────────────────────────────────────────────────

    @api.model
    def _find_by_technical_name(self, technical_name):
        """Look up a task by technical name. Empty recordset if none."""
        return self.search([
            ('technical_name', '=', technical_name),
        ], limit=1)
