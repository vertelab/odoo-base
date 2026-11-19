# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

"""Test-only model: methods that poison the transaction on purpose.

`cron.task` calls a method by name on a model. To reproduce the production
failure (a database error leaving the transaction in
`InFailedSqlTransaction`) the test needs a method that actually triggers one
— patching `_run` would bypass the very code path under test.

Only loaded in test mode (`__manifest__` does not reference this file).
"""

from odoo import models


class CronTickPoisonProbe(models.AbstractModel):
    """Methods used by the cron_tick tests to simulate a poisoned run."""

    _name = 'cron.tick.poison.probe'
    _description = 'cron_tick test probe (poisons the transaction)'

    def poison_then_raise(self):
        """Trigger a real database error, then raise.

        `SELECT 1/0` is a genuine PostgreSQL error: it aborts the transaction
        exactly the way a `lock timeout` or a `deadlock detected` does. That
        is the condition `_ensure_usable_transaction()` exists to recover
        from — a Python exception would not reproduce it.
        """
        self.env.cr.execute('SELECT 1/0')
        return True

    def succeed(self):
        """A no-op that always succeeds — the control task in a tick."""
        return True

    def write_a_param_and_succeed(self):
        """Write something and succeed. The engine must KEEP the write.

        Regression for 2026-11-19: `_close_savepoint_safely` was called with
        a hardcoded `rollback=True` from a `finally` block that runs on both
        paths, so every SUCCESSFUL task had its own work rolled back. The
        task reported `status=ok` while everything it wrote disappeared —
        `storage_collect` measured 46 minions, logged them, saved its cursor,
        and the cursor was gone.

        `last_run` and `failure_count` are written AFTER the savepoint, which
        is exactly why the old tests missed it: they asserted on the status,
        not on the work. This method writes INSIDE the savepoint so a test
        can prove the write survives.

        The key is per-call so parallel tests do not collide.
        """
        key = 'cron_tick.test.savepoint_release.%s' % self.env.cr.dbname
        self.env['ir.config_parameter'].sudo().set_param(key, 'kept')
        return True

    def write_a_param_then_raise(self):
        """Write something, then fail. The engine must DISCARD the write.

        The mirror of the method above: a failed run must not leave partial
        writes behind. Together they pin both sides of the rollback flag.
        """
        key = 'cron_tick.test.savepoint_rollback.%s' % self.env.cr.dbname
        self.env['ir.config_parameter'].sudo().set_param(key, 'discarded')
        raise ValueError('deliberate failure after a write')

    def poison_and_release_savepoint(self):
        """Abort the transaction AND leave the engine's savepoint unusable.

        This is the shape that broke production on 2026-11-12: the task hits
        a database error, PostgreSQL aborts the transaction, and the
        savepoint the engine opened can no longer be closed. Before
        `_close_savepoint_safely`, the cleanup raised
        `InvalidSavepointSpecification` and that exception replaced the
        task's own error — the tick died and every following task stayed
        stuck.

        `SELECT 1/0` aborts the transaction; the explicit `ROLLBACK TO` in
        the caller's cleanup is what then fails. No table locks, no external
        state — safe to run anywhere.
        """
        self.env.cr.execute('SELECT 1/0')
        return True
