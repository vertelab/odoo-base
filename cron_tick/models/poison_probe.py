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
