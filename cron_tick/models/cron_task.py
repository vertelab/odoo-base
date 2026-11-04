# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

"""cron.task — declarative scheduling.

One record per scheduled task. Modules declare their tasks as data XML;
this module owns the engine. The engine knows nothing about any task.

CADENCE, NOT INTERVAL — WITH AN ESCAPE HATCH
    A task states *which* cadence it belongs to (min/hour/daily/week/month),
    not an interval in seconds. That removes the per-task `next_run`
    arithmetic and the entire class of calculation errors (wrong timedelta,
    wrong timezone, forgotten next_run on failure). Only the tick needs to
    know when to run.

    A task may instead set `interval_number`/`interval_type` when the five
    cadences cannot express the interval it needs (15 minutes, 6 hours,
    14 days). Such a task is carried by the `min` tick and runs when its own
    interval has elapsed. The two are mutually exclusive: a task sets a
    cadence XOR an interval.

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

from odoo import _, SUPERUSER_ID, api, fields, models
from odoo.exceptions import UserError, ValidationError

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
    _inherit = ['mail.thread', 'mail.activity.mixin']

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
    ], index=True, tracking=True,
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
    active = fields.Boolean(
        default=True, tracking=True,
        help='Deactivated automatically after `max_failures` consecutive '
             'failures. Re-activate to resume scheduling.')

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
    run_log_count = fields.Integer(
        compute='_compute_run_log_count',
        help='Number of run log records for this task.')

    _sql_constraints = [
        ('technical_name_uniq', 'UNIQUE(technical_name)',
         'The technical name must be unique — it is the identity of the task.'),
    ]

    # NOTE: the cadence/interval XOR is enforced in Python (`_check_schedule`),
    # not as a SQL CHECK. A CHECK fires before `@api.constrains` and surfaces
    # as a raw psycopg2 error, so the readable message would never be shown.
    # `cron.task` records are created from module data, not free input, so the
    # Python constraint is the only validation path that matters.

    # ───────────────────────────────────────────────────────────────────
    # Computed fields
    # ───────────────────────────────────────────────────────────────────

    @api.constrains('cadence', 'interval_number', 'interval_type')
    def _check_schedule(self):
        """Exactly one of cadence / interval must be set.

        NOTE: `@api.constrains` only fires when one of the named fields is
        present in `vals`. `create()` with neither field would therefore
        pass unvalidated, so `create()` calls this explicitly — see
        `create()` below. This constraint covers `write()`.
        """
        for task in self:
            task._validate_schedule()

    def _validate_schedule(self):
        """Validate the schedule fields on a single record."""
        self.ensure_one()
        has_cadence = bool(self.cadence)
        has_interval = bool(self.interval_type)
        if has_cadence and has_interval:
            raise ValidationError(_(
                'The task "%s" has both a cadence and an interval. Set '
                'one of them.') % self.technical_name)
        if not has_cadence and not has_interval:
            raise ValidationError(_(
                'The task "%s" has neither a cadence nor an interval. '
                'Set one of them.') % self.technical_name)
        if has_interval and not self.interval_number:
            raise ValidationError(_(
                'The task "%s" has an interval type but no interval '
                'number.') % self.technical_name)

    @api.model_create_multi
    def create(self, vals_list):
        """Validate the schedule on create.

        `@api.constrains` does not fire when none of its fields appear in
        `vals`, so a task created without a cadence AND without an interval
        would slip through. Validate explicitly here.
        """
        tasks = super().create(vals_list)
        for task in tasks:
            task._validate_schedule()
        return tasks

    @api.depends('locked_by')
    def _compute_is_locked(self):
        for task in self:
            task.is_locked = bool(task.locked_by)

    @api.depends('last_run', 'cadence', 'interval_number', 'interval_type',
                 'active')
    def _compute_is_overdue(self):
        now = fields.Datetime.now()
        for task in self:
            if not task.active or not task.last_run:
                task.is_overdue = False
                continue
            if task.interval_type:
                limit = task._interval_seconds() * 3
            else:
                limit = CADENCE_SECONDS.get(task.cadence, 86400) * 3
            task.is_overdue = (now - task.last_run).total_seconds() > limit

    def _compute_run_log_count(self):
        """Count run log records per task (smart button).

        `read_group` in one query instead of one `search_count` per record —
        the list view reads the field for every row.
        """
        counts = {}
        if self.ids:
            try:
                groups = self.env['cron.task.log'].sudo().read_group(
                    [('task_id', 'in', self.ids)], ['task_id'], ['task_id'])
                counts = {g['task_id'][0]: g['task_id_count'] for g in groups
                          if g.get('task_id')}
            except Exception:  # noqa: BLE001 — never break the form over a count
                _logger.exception(
                    'cron.task: could not count run logs for %s', self.ids)
                counts = {}
        for task in self:
            task.run_log_count = counts.get(task.id, 0)

    @api.depends('cadence', 'interval_number', 'interval_type')
    def _compute_cadence_label(self):
        labels = dict(self._fields['cadence'].selection)
        type_labels = dict(self._fields['interval_type'].selection)
        for task in self:
            if task.interval_type:
                unit = type_labels.get(task.interval_type, task.interval_type)
                task.cadence_label = 'Every %s %s' % (
                    task.interval_number or '?', unit.lower())
            else:
                task.cadence_label = labels.get(
                    task.cadence, task.cadence or '')

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

        # Interval tasks cannot be expressed as a domain: the threshold
        # depends on interval_number * interval_type per record. Search on
        # the cadence branches only and let the caller over-fetch; the
        # computed field is always correct when read on a record.
        branches.append([
            ('interval_type', '!=', False),
            ('last_run', '!=', False),
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

    def _interval_seconds(self):
        """The task's interval in seconds (0 when it uses a cadence)."""
        self.ensure_one()
        if not self.interval_type or not self.interval_number:
            return 0
        return (INTERVAL_SECONDS.get(self.interval_type, 0)
                * self.interval_number)

    # ───────────────────────────────────────────────────────────────────
    # Cadence logic (D7)
    # ───────────────────────────────────────────────────────────────────

    def _is_due(self, now=None):
        """Is the task due?

        Two modes, mutually exclusive (see `_check_schedule`):

        INTERVAL MODE (`interval_number`/`interval_type` set)
            Due when the interval has elapsed since the last run. Measured
            from `last_run`, so a slow run does not drift the schedule —
            the next run is N units after the previous one FINISHED.

        CADENCE MODE (`cadence` set)
            `min`/`hour` are governed by the time elapsed since the last run.
            `daily`/`week`/`month` are governed by the spread window — the
            task runs when the window has opened and it has not already run
            in the period.
        """
        self.ensure_one()
        now = now or fields.Datetime.now()

        if self.interval_type:
            if not self.last_run:
                return True
            seconds = self._interval_seconds()
            return (now - self.last_run).total_seconds() >= seconds

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

    def _execute(self, owner='manual', trigger=None, trigger_detail=None):
        """Run the task with locking, measuring and recording.

        This is the common path for all three trigger types. Returns a dict
        with status and duration.

        `trigger` defaults to `manual` — the webhook passes `webhook`.
        """
        self.ensure_one()
        trigger = trigger or 'manual'
        user = self.env.user if trigger == 'manual' else None
        result = self._run_locked_task(
            self.id, owner=owner, trigger=trigger,
            trigger_detail=trigger_detail or (user.name if user else None),
            user_id=user.id if user else None)
        if result['status'] == 'locked':
            return {
                'status': 'locked',
                'technical_name': self.technical_name,
            }
        if result['status'] == 'error':
            return {
                'status': 'error',
                'technical_name': self.technical_name,
                'duration_ms': result['duration_ms'],
                'error': result['error'],
            }
        return {
            'status': 'ok',
            'technical_name': self.technical_name,
            'duration_ms': result['duration_ms'],
        }

    def _run_locked_task(self, task_id, owner, trigger, trigger_detail=None,
                         user_id=None):
        """The ONE run path: lock → savepoint → run → record → log.

        Shared by the tick engine and `_execute` (webhook/manual), so the two
        paths cannot drift apart. Returns a dict:

            {'status': 'ok'|'error'|'locked', 'duration_ms': int,
             'error': str|None}

        WARNING: after a rolled-back savepoint the ORM cache is corrupt —
        `invalidate_all()` + `browse(task_id)` is mandatory before writing
        the error (see README).

        `user_id` is an ID and not a recordset on purpose: a parameter named
        `user` holding a recordset breaks `_()` (Odoo's translation helper
        inspects the caller's locals and calls `int()` on a `user` it finds
        there). See README, "Troubleshooting".
        """
        task = self.browse(task_id)
        if not task._acquire_lock(owner):
            # Refused: the method was NOT called. Record it so a task that
            # never runs because of a stuck lock is visible in the log.
            task.browse(task_id)._log_run_record(
                'locked', trigger, trigger_detail,
                text=_('Already running (%s) — not started.') % (
                    task.locked_by or _('unknown')))
            return {'status': 'locked', 'duration_ms': 0, 'error': None}
        started = time.monotonic()
        try:
            try:
                with self.env.cr.savepoint():
                    task._run()
            except Exception as exc:  # noqa: BLE001 — the engine catches all
                duration_ms = int((time.monotonic() - started) * 1000)
                self.env.invalidate_all()
                failed = self.browse(task_id)
                failed._record_failure(exc, duration_ms)
                failed._log_run_record(
                    'error', trigger, trigger_detail,
                    duration_ms=duration_ms, text=str(exc), user_id=user_id)
                _logger.exception(
                    'cron.task %s failed (%s ms)',
                    failed.technical_name, duration_ms)
                return {
                    'status': 'error',
                    'duration_ms': duration_ms,
                    'error': str(exc),
                }
            duration_ms = int((time.monotonic() - started) * 1000)
            self.env.invalidate_all()
            done = self.browse(task_id)
            done._record_success(duration_ms)
            done._log_run_record(
                'ok', trigger, trigger_detail,
                duration_ms=duration_ms,
                text=_('Ran in %s ms.') % duration_ms, user_id=user_id)
            if duration_ms > done.timeout_seconds * 1000:
                _logger.warning(
                    'cron.task %s exceeded the time limit: %s ms > %s s',
                    done.technical_name, duration_ms, done.timeout_seconds)
            return {'status': 'ok', 'duration_ms': duration_ms, 'error': None}
        finally:
            # Release the advisory lock EVEN on error — otherwise it is held
            # until the connection closes and the task can never run again.
            self.browse(task_id)._release_lock()

    def _log_run_record(self, status, trigger, trigger_detail=None,
                        duration_ms=0, text=None, user_id=None):
        """Write one run log record. Never raises."""
        self.ensure_one()
        try:
            self.env['cron.task.log']._log_run(
                self, status=status, trigger=trigger,
                trigger_detail=trigger_detail, duration_ms=duration_ms,
                text=text, user_id=user_id)
        except Exception:  # noqa: BLE001 — history must never break a run
            _logger.exception(
                'cron.task %s: could not write the run log', self.technical_name)

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
        previous_count = self.failure_count
        count = previous_count + 1
        deactivated = count >= self.max_failures
        vals = {
            'last_run': fields.Datetime.now(),
            'last_duration_ms': duration_ms,
            'failure_count': count,
            'last_error': str(exc)[:4000],
            'locked_by': False,
            'locked_at': False,
        }
        if deactivated:
            vals['active'] = False
            _logger.error(
                'cron.task %s deactivated after %s consecutive failures',
                self.technical_name, count)
        self.write(vals)

        # Chatter: only the events a human needs to see. Repeating failures in
        # the same streak produce a run log record but no new message — see
        # design D6. `message_post` must never change the run result.
        try:
            if deactivated:
                self.message_post(body=_(
                    'Deactivated automatically after %(count)s consecutive '
                    'failures. Last error: %(error)s',
                    count=count, error=str(exc)[:500]))
            elif previous_count == 0:
                self.message_post(body=_(
                    'First failure in a new streak: %s', str(exc)[:500]))
        except Exception:  # noqa: BLE001 — chatter must not break the run
            _logger.exception(
                'cron.task %s: could not post the failure to chatter',
                self.technical_name)

    def write(self, vals):
        """Post a chatter message when a task is re-activated manually.

        Auto-deactivation is posted by `_record_failure`; this covers the
        human action of switching a deactivated task back on, which is
        otherwise an invisible state change.
        """
        was_inactive = {task.id for task in self if not task.active}
        result = super().write(vals)
        if vals.get('active') and was_inactive:
            # `with_user(SUPERUSER_ID)` is required: `base.group_user` has
            # read-only access to `cron.task`, so a non-admin re-activation
            # would otherwise fail on the message write.
            for task in self.with_user(SUPERUSER_ID):
                if task.id in was_inactive:
                    try:
                        task.message_post(body=_(
                            'Re-activated manually by %s.', self.env.user.name))
                    except Exception:  # noqa: BLE001
                        _logger.exception(
                            'cron.task %s: could not post re-activation',
                            task.technical_name)
        return result

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
            # A task belongs to exactly one tick: the one named by its
            # cadence, or the interval tick when it uses an interval.
            if cadence == INTERVAL_TICK_CADENCE:
                domain = [
                    ('active', '=', True),
                    '|',
                    ('cadence', '=', cadence),
                    ('interval_type', '!=', False),
                ]
            else:
                domain = [
                    ('active', '=', True),
                    ('cadence', '=', cadence),
                ]
            candidates = self.search(domain, order='sequence, id')
            due = candidates.filtered(lambda t: t._is_due(now))

            ran, failed, locked = 0, 0, 0
            for task in due:
                # One run path for tick, webhook and manual — see
                # `_run_locked_task`. It acquires and releases the task lock,
                # records the run history and writes the run log.
                result = self._run_locked_task(
                    task.id, owner='tick:%s' % cadence, trigger='tick',
                    trigger_detail=cadence)
                if result['status'] == 'locked':
                    locked += 1
                elif result['status'] == 'error':
                    # `_run_locked_task` already logged the traceback; a
                    # second `_logger.exception` here would print it twice.
                    _logger.info(
                        'cron.task %s failed in tick %s: %s',
                        task.technical_name, cadence, result.get('error'))
                    failed += 1
                else:
                    ran += 1

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

    def action_view_run_logs(self):
        """Smart button: open the run log filtered on this task."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Run Log'),
            'res_model': 'cron.task.log',
            'view_mode': 'list,form',
            'domain': [('task_id', '=', self.id)],
            'context': {'default_task_id': self.id},
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
