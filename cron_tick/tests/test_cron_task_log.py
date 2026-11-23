# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

"""Tests for the cron.task run log and the chatter integration.

WARNING: advisory locks are re-entrant within the same session, so a test in
one TransactionCase cannot prove mutual exclusion. The `locked` tests here
patch `_acquire_lock` instead — that is the documented way to simulate a
second worker.
"""

from datetime import timedelta
from unittest import mock

import psycopg2
from odoo import fields
from odoo.modules.registry import Registry
from odoo.tests.common import TransactionCase


class CronTaskTestBase(TransactionCase):

    def setUp(self):
        super().setUp()
        self.Task = self.env['cron.task']
        self.Log = self.env['cron.task.log']
        # A model/method pair that always succeeds.
        self.task_ok = self.Task.create({
            'name': 'Test ok',
            'technical_name': 'test_ok',
            'model_name': 'cron.task.log',
            'method_name': '_retention_days',
            'cadence': 'hour',
            'module': 'cron_tick',
        })
        # A model/method pair that always raises.
        self.task_fail = self.Task.create({
            'name': 'Test fail',
            'technical_name': 'test_fail',
            'model_name': 'cron.task.log',
            'method_name': '_no_such_method_here',
            'cadence': 'hour',
            'module': 'cron_tick',
        })

    def logs_of(self, task):
        return self.Log.search([('task_id', '=', task.id)])

    def notes_of(self, task):
        """The messages this module posted to the task's chatter.

        `message_post()` without an explicit subtype creates a `notification`
        message with the internal "Note" subtype — NOT `message_type ==
        'comment'` (verified: a fresh task shows only 'Scheduled Task
        created' + our note, both as `notification`). Filtering on 'comment'
        silently returned nothing and made every chatter test vacuous.

        Empty-bodied notes are filtered out as well: Odoo's tracking posts a
        note with no body text (only `tracking_value_ids`) when a tracked
        field changes — that is the `active`/`cadence` tracking, not a
        message we wrote. See design D6.

        The creation message (also a note) is excluded by WHEN it was
        posted, not by its text. The old filter compared against the English
        source string `'Scheduled Task created'`, which silently stopped
        working on a database with Swedish translations active — the body
        reads "Schemalagd uppgift skapades" and every assertion got one note
        too many. Measured 2026-11-11: four chatter tests failed on a Swedish
        test database while passing on an English one.

        The creation message is the FIRST one on the record — `mail.thread`
        posts it from `create()`, so it always has the lowest id and nothing
        we write can precede it. Excluding the lowest id is deterministic and
        language-independent, which is what the original docstring promised
        but the code did not do (it compared the English source string, and
        got one note too many on a Swedish database).

        Timestamps cannot be used here: the whole test runs within the same
        second, so the creation note and our note share `date`.
        """
        notes = task.message_ids.filtered(
            lambda m: m.message_type == 'notification'
            and m.subtype_id.internal
            and (m.body or '').strip())
        if not notes:
            return notes
        first = notes.sorted('id')[0]
        return notes - first


class TestRunLog(CronTaskTestBase):

    def test_success_writes_one_log(self):
        """A successful run leaves exactly one `ok` record."""
        result = self.task_ok._execute(owner='test', trigger='manual')
        self.assertEqual(result['status'], 'ok')
        logs = self.logs_of(self.task_ok)
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs.status, 'ok')
        self.assertEqual(logs.trigger, 'manual')
        self.assertGreaterEqual(logs.duration_ms, 0)
        self.assertTrue(logs.text)

    def test_failure_writes_one_log_with_error(self):
        """A failed run leaves exactly one `error` record with the message."""
        result = self.task_fail._execute(owner='test', trigger='manual')
        self.assertEqual(result['status'], 'error')
        logs = self.logs_of(self.task_fail)
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs.status, 'error')
        self.assertIn('_no_such_method_here', logs.text or '')

    def test_webhook_trigger_is_recorded(self):
        """The webhook path records `trigger = webhook`, not `manual`."""
        self.task_ok._execute(owner='webhook', trigger='webhook')
        logs = self.logs_of(self.task_ok)
        self.assertEqual(logs.trigger, 'webhook')
        self.assertFalse(logs.user_id)

    def test_manual_run_records_user(self):
        """A manual run records who pressed the button."""
        self.task_ok.action_run_now()
        logs = self.logs_of(self.task_ok)
        self.assertEqual(logs.trigger, 'manual')
        self.assertEqual(logs.user_id, self.env.user)

    def test_locked_run_is_logged_and_not_executed(self):
        """A refused run logs `locked` and never calls the method."""
        with mock.patch.object(
                type(self.task_ok), '_acquire_lock', return_value=False):
            result = self.task_ok._execute(owner='test', trigger='manual')
        self.assertEqual(result['status'], 'locked')
        logs = self.logs_of(self.task_ok)
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs.status, 'locked')
        self.assertEqual(logs.duration_ms, 0)

    def test_history_survives_a_later_success(self):
        """error then ok → two records, both kept."""
        self.task_fail._execute(owner='test', trigger='manual')
        # Point the same task at a method that works and run again.
        self.task_fail.write({'model_name': 'cron.task.log',
                              'method_name': '_retention_days'})
        self.task_fail._execute(owner='test', trigger='manual')
        logs = self.logs_of(self.task_fail)
        self.assertEqual(len(logs), 2)
        self.assertEqual(set(logs.mapped('status')), {'ok', 'error'})

    def test_tick_writes_logs(self):
        """The tick engine writes the same records as the manual path."""
        self.task_ok.write({'cadence': 'min'})
        # Keep the tick cheap: only this task is due.
        with mock.patch.object(type(self.task_ok), '_is_due',
                               side_effect=lambda now: True):
            self.task_ok._cron_tick('min')
        logs = self.logs_of(self.task_ok)
        self.assertTrue(logs)
        mine = logs.filtered(lambda log: log.task_id == self.task_ok)
        self.assertTrue(mine)
        self.assertEqual(set(mine.mapped('trigger')), {'tick'})
        self.assertEqual(set(mine.mapped('status')), {'ok'})

    def test_log_snapshot_fields(self):
        """The log keeps the task identity even after a rename."""
        self.task_ok._execute(owner='test', trigger='manual')
        log = self.logs_of(self.task_ok)
        old_name = log.task_name
        self.task_ok.write({'name': 'Renamed'})
        self.assertEqual(log.task_name, old_name)
        self.assertEqual(log.technical_name, 'test_ok')

    def test_newest_first(self):
        """The default order is newest run first."""
        self.task_ok._execute(owner='test', trigger='manual')
        self.task_ok._execute(owner='test', trigger='manual')
        logs = self.logs_of(self.task_ok)
        self.assertEqual(len(logs), 2)
        self.assertGreaterEqual(logs[0].run_at, logs[1].run_at)


class TestRetention(CronTaskTestBase):

    def _make_log(self, days_ago):
        return self.Log.sudo().create({
            'task_id': self.task_ok.id,
            'task_name': self.task_ok.name,
            'technical_name': self.task_ok.technical_name,
            'run_at': fields.Datetime.now() - timedelta(days=days_ago),
            'status': 'ok',
            'trigger': 'tick',
        })

    def test_old_records_deleted_new_kept(self):
        """Only records older than the window are removed."""
        self.env['ir.config_parameter'].sudo().set_param(
            'cron_tick.log_retention_days', '90')
        old = self._make_log(120)
        fresh = self._make_log(5)
        self.Log._cron_cleanup()
        self.assertFalse(old.exists())
        self.assertTrue(fresh.exists())

    def test_retention_value_is_respected(self):
        """Lowering the window deletes more."""
        self.env['ir.config_parameter'].sudo().set_param(
            'cron_tick.log_retention_days', '7')
        ten_days = self._make_log(10)
        two_days = self._make_log(2)
        self.Log._cron_cleanup()
        self.assertFalse(ten_days.exists())
        self.assertTrue(two_days.exists())

    def test_zero_disables_cleanup(self):
        """0 is the rollback switch — nothing is deleted."""
        self.env['ir.config_parameter'].sudo().set_param(
            'cron_tick.log_retention_days', '0')
        old = self._make_log(400)
        result = self.Log._cron_cleanup()
        self.assertTrue(result['disabled'])
        self.assertTrue(old.exists())

    def test_invalid_value_falls_back_to_default(self):
        """A garbage parameter falls back to 90 days, not to a crash."""
        self.env['ir.config_parameter'].sudo().set_param(
            'cron_tick.log_retention_days', 'not-a-number')
        self.assertEqual(self.Log._retention_days(), 90)

    def test_cleanup_is_a_task(self):
        """The cleanup is registered as a daily cron.task."""
        task = self.Task.search(
            [('technical_name', '=', 'cron_log_cleanup')], limit=1)
        self.assertTrue(task)
        self.assertEqual(task.cadence, 'daily')
        self.assertEqual(task.model_name, 'cron.task.log')
        self.assertEqual(task.method_name, '_cron_cleanup')


class TestChatter(CronTaskTestBase):

    def test_first_failure_posts_message(self):
        """The first failure in a streak posts one chatter message."""
        self.task_fail._execute(owner='test', trigger='manual')
        notes = self.notes_of(self.task_fail)
        self.assertEqual(len(notes), 1)
        self.assertIn('_no_such_method_here', notes[0].body or '')

    def test_repeated_failure_does_not_spam(self):
        """A second failure in the same streak posts nothing new."""
        self.task_fail.write({'max_failures': 10})  # keep it active
        self.task_fail._execute(owner='test', trigger='manual')
        self.task_fail._execute(owner='test', trigger='manual')
        self.assertEqual(len(self.notes_of(self.task_fail)), 1)
        # …but both runs are in the log.
        self.assertEqual(len(self.logs_of(self.task_fail)), 2)

    def test_auto_deactivation_posts_message(self):
        """Reaching max_failures posts a deactivation message."""
        self.task_fail.write({'max_failures': 1})
        self.task_fail._execute(owner='test', trigger='manual')
        self.assertFalse(self.task_fail.active)
        notes = self.notes_of(self.task_fail)
        # One message: `_record_failure` posts the deactivation branch and
        # skips the first-failure branch — the deactivation IS the first
        # failure in the streak when `max_failures` is 1 (design D6).
        self.assertEqual(len(notes), 1)
        self.assertIn('_no_such_method_here', notes[0].body or '')

    def test_reactivation_posts_message(self):
        """Switching a deactivated task back on is visible in chatter."""
        self.task_fail.write({'active': False})
        self.task_fail.write({'active': True})
        notes = self.notes_of(self.task_fail)
        self.assertEqual(len(notes), 1)
        self.assertIn(self.env.user.name, notes[0].body or '')

    def test_chatter_failure_does_not_break_the_run(self):
        """A broken message_post must not turn a run into an error."""
        with mock.patch.object(
                type(self.task_ok), 'message_post', side_effect=Exception('x')):
            self.task_ok.write({'max_failures': 1})
            self.task_ok._execute(owner='test', trigger='manual')
        # The successful run is still recorded as ok.
        logs = self.logs_of(self.task_ok)
        self.assertEqual(logs.status, 'ok')


class TestSmartButton(CronTaskTestBase):

    def test_run_log_count(self):
        """The smart button counts the task's own records."""
        self.task_ok._execute(owner='test', trigger='manual')
        self.task_ok._execute(owner='test', trigger='manual')
        self.task_ok.invalidate_recordset(['run_log_count'])
        self.assertEqual(self.task_ok.run_log_count, 2)

    def test_action_domain_filters_on_task(self):
        """The action opens the log filtered on the task."""
        self.task_ok._execute(owner='test', trigger='manual')
        self.task_fail._execute(owner='test', trigger='manual')
        action = self.task_ok.action_view_run_logs()
        self.assertEqual(action['res_model'], 'cron.task.log')
        found = self.Log.search(action['domain'])
        self.assertEqual(len(found), 1)
        self.assertEqual(found.task_id, self.task_ok)

    def test_empty_history_counts_zero(self):
        """A task that never ran counts 0."""
        self.task_ok.invalidate_recordset(['run_log_count'])
        self.assertEqual(self.task_ok.run_log_count, 0)


class TestAccess(TransactionCase):

    def test_internal_user_can_read_but_not_write(self):
        """`base.group_user` reads the log, cannot create or unlink."""
        user = self.env['res.users'].create({
            'name': 'Cron Reader',
            'login': 'cron_reader_test',
            # `groups_id` is the Odoo 18 field name (`group_ids` is 19+).
            'groups_id': [(6, 0, [self.env.ref('base.group_user').id])],
        })
        log = self.env['cron.task.log'].sudo().create({
            'task_id': self.env['cron.task'].sudo().create({
                'name': 'Access test',
                'technical_name': 'access_test',
                'model_name': 'cron.task.log',
                'method_name': '_retention_days',
                'cadence': 'hour',
            }).id,
            'run_at': fields.Datetime.now(),
            'status': 'ok',
            'trigger': 'tick',
        })
        LogAsUser = self.env['cron.task.log'].with_user(user)
        self.assertTrue(LogAsUser.search([('id', '=', log.id)]))
        with self.assertRaises(Exception):
            LogAsUser.create({'task_id': log.task_id.id,
                              'status': 'ok', 'trigger': 'tick'})
        with self.assertRaises(Exception):
            LogAsUser.browse(log.id).unlink()


class TestFailureRecordingInPoisonedTransaction(CronTaskTestBase):
    """`_record_failure` must survive a transaction PostgreSQL already aborted.

    Measured in production 2026-11-11: a `lock timeout` on an INSERT left the
    transaction in `InFailedSqlTransaction`. `cursor.savepoint()` could not
    help — `_FlushingSavepoint.__init__` calls `cr.flush()` before issuing
    `SAVEPOINT`, so `__enter__` raised and nothing was rolled back.
    `_record_failure` then raised on `self.failure_count`, the exception
    escaped `_cron_tick`, and the whole tick transaction — including every
    `nextcall` update — was rolled back. Tick 991 reached failure_count 471
    and 18 of 80 active crons sat with a `nextcall` in the past for over an
    hour.
    """

    def _poison(self):
        """Abort the transaction the way a database error does."""
        with self.assertRaises(psycopg2.Error):
            self.env.cr.execute('SELECT 1/0')

    def test_record_failure_survives_poisoned_transaction(self):
        """The whole point: no raise, and the counter still advances."""
        before = self.task_fail.failure_count
        self._poison()
        # Must not raise. Before the fix this raised InFailedSqlTransaction.
        self.task_fail._record_failure(Exception('simulated'), 42)
        self.assertEqual(self.task_fail.failure_count, before + 1)
        self.assertIn('simulated', self.task_fail.last_error or '')

    def test_transaction_is_usable_after_recording(self):
        """Recovery must leave the connection usable, not just swallow the error."""
        self._poison()
        self.task_fail._record_failure(Exception('simulated'), 0)
        # A plain query proves the transaction left InFailedSqlTransaction.
        self.env.cr.execute('SELECT 1')
        self.assertEqual(self.env.cr.fetchone()[0], 1)

    def test_healthy_transaction_is_untouched(self):
        """No regression: the probe must not roll back a working transaction."""
        before = self.task_fail.failure_count
        self.task_fail._record_failure(Exception('simulated'), 7)
        self.assertEqual(self.task_fail.failure_count, before + 1)
        self.assertIn('simulated', self.task_fail.last_error or '')

    def test_deactivation_still_works_after_recovery(self):
        """The deactivation path must run too — it is the reason to record."""
        self.task_fail.write({'max_failures': 1})
        self._poison()
        self.task_fail._record_failure(Exception('simulated'), 0)
        self.assertFalse(self.task_fail.active)

    def test_original_error_is_preserved(self):
        """`last_error` reports the task's error, not the recovery's.

        The recovery logs its own warning, but the reason the task failed must
        survive — otherwise an operator sees "transaction aborted" and never
        learns what actually broke.
        """
        self._poison()
        self.task_fail._record_failure(ValueError('the real reason'), 0)
        self.assertIn('the real reason', self.task_fail.last_error or '')


class TestPoisonedTaskInTick(CronTaskTestBase):
    """The blast radius of a poisoned task must be exactly one task.

    Production 2026-11-11: when `_record_failure` hit an aborted transaction
    the exception escaped `_cron_tick` and rolled back the whole tick —
    including the `nextcall` of every task already run. One broken task
    stopped the scheduler for over an hour (18 of 80 crons stuck).

    These tests run the real `_cron_tick` with a task that poisons the
    transaction from inside its own body, which is the production trigger.
    """

    def _make_task(self, name, method, sequence=10):
        return self.Task.create({
            'name': name,
            'technical_name': name.replace(' ', '_').lower(),
            'model_name': 'cron.tick.poison.probe',
            'method_name': method,
            'cadence': 'min',
            'sequence': sequence,
            'module': 'cron_tick',
        })

    def _run_min_tick(self):
        """Run the `min` tick with ONLY this test's tasks due.

        `CronTaskTestBase` already created `task_fail` (a method that does not
        exist) on the `min` cadence. It would fail in the same tick and make
        the counters meaningless, so it is parked on another cadence for the
        duration of the test.
        """
        self.task_fail.write({'cadence': 'week'})
        self.task_ok.write({'cadence': 'week'})
        return self.Task._cron_tick('min')

    def test_tick_continues_after_poisoned_task(self):
        """A poisoned task must not prevent the next task from running."""
        poison = self._make_task('Poison first', 'poison_then_raise', 1)
        after = self._make_task('Runs after', 'succeed', 2)

        result = self._run_min_tick()

        # The poisoned task is reported as failed...
        self.assertEqual(result['failed'], 1)
        # ...and the task after it still ran.
        self.assertEqual(
            after.failure_count, 0,
            'the task after a poisoned one must not be marked failed')
        self.assertTrue(after.last_run, 'the following task never ran')
        self.assertEqual(
            poison.failure_count, 1,
            'the poisoned task must be recorded as failed')

    def test_run_log_written_after_poisoned_task(self):
        """The run log must get an `error` row even after a poisoned run.

        The log is the only place an operator can see that the task failed —
        `last_error` shows just the latest. If the poison swallowed the log
        write there would be no trace at all.
        """
        poison = self._make_task('Poison logged', 'poison_then_raise', 1)

        self._run_min_tick()

        logs = self.logs_of(poison)
        self.assertEqual(len(logs), 1, 'no run log was written')
        self.assertEqual(logs[0].status, 'error')
        # The text is the PostgreSQL error the probe raises (`SELECT 1/0`),
        # not the task's name — assert on that, not on a guessed string.
        self.assertIn('division by zero', (logs[0].text or '').lower())

    def test_following_task_keeps_its_run_record(self):
        """The task before a poisoned one keeps its own run record.

        This is the regression that mattered in production: `cr.rollback()`
        discards everything in the transaction, so the recovery has to happen
        *after* the earlier tasks have been accounted for. If the rollback
        runs before they are recorded, their `last_run` disappears and they
        look like they never ran.
        """
        before = self._make_task('Runs before', 'succeed', 1)
        self._make_task('Poison second', 'poison_then_raise', 2)

        self._run_min_tick()

        self.assertTrue(
            before.last_run,
            'the task that ran before the poisoned one lost its run record — '
            'the recovery rolled back too much')
        self.assertEqual(before.failure_count, 0)

    def test_record_failure_survives_dead_connection(self):
        """A closed connection must not raise either.

        Measured 2026-11-11: `ai_cost_aggregate` was killed by
        `psycopg2.DatabaseError: out of memory for query result`, and the
        connection was already closed when `_record_failure` ran. The
        rollback then raised `InterfaceError: connection already closed`,
        which escaped into `_cron_tick` and stopped the tick — the same
        cascade the fix exists to prevent, through a second door.

        Nothing can be recorded on a dead connection; the contract is that
        the scheduler keeps running.
        """
        with mock.patch.object(
                type(self.env.cr), 'rollback',
                side_effect=psycopg2.InterfaceError('connection already closed')):
            # Must not raise.
            self.task_fail._record_failure(Exception('simulated'), 0)


class TestSavepointCleanup(CronTaskTestBase):
    """The engine must clean up its own savepoint without deciding the run.

    Production 2026-11-12: `ai_okf_index_dirty` hit `canceling statement due
    to lock timeout` inside `_run()`. PostgreSQL aborted the transaction, so
    `_FlushingSavepoint.__init__`'s `cr.flush()` (or the cleanup's
    `ROLLBACK TO`/`RELEASE`) raised `InvalidSavepointSpecification` — and that
    exception replaced the task's own error on the way out. The tick died and
    69 tasks sat stuck for five days.

    Closing the savepoint is CLEANUP. It must never decide the outcome, and
    it must never replace the task's real error.
    """

    def _make_task(self, name, method, sequence=10, cadence='week'):
        return self.Task.create({
            'name': name,
            'technical_name': name.replace(' ', '_').lower(),
            'model_name': 'cron.tick.poison.probe',
            'method_name': method,
            'cadence': cadence,
            'sequence': sequence,
            'module': 'cron_tick',
        })

    def test_run_survives_unclosable_savepoint(self):
        """A savepoint that cannot be closed must not raise out of the run path."""
        task = self._make_task('Unclosable savepoint', 'poison_then_raise')
        # Must not raise. Before the fix this raised InvalidSavepointSpecification.
        result = task._execute(owner='test', trigger='manual')
        self.assertEqual(result['status'], 'error')

    def test_original_error_survives_failed_cleanup(self):
        """The reported error is the task's, not the cleanup's."""
        task = self._make_task('Error preserved', 'poison_then_raise')
        result = task._execute(owner='test', trigger='manual')
        self.assertIn('division by zero', result['error'])
        self.assertNotIn('savepoint', result['error'].lower())
        self.assertIn('division by zero', task.last_error or '')

    def test_failure_is_recorded_despite_failed_cleanup(self):
        """The counter still advances — that is what deactivation depends on."""
        task = self._make_task('Counter advances', 'poison_then_raise')
        before = task.failure_count
        task._execute(owner='test', trigger='manual')
        self.assertEqual(task.failure_count, before + 1)

    def test_close_savepoint_safely_reports_dead_savepoint(self):
        """A savepoint that does not exist is reported, not raised.

        Runs on a SEPARATE cursor: the test framework forbids `cr.rollback()`
        on the test's own cursor (it would break the outer test transaction),
        and recovering from an aborted transaction requires exactly that.
        """
        with Registry(self.env.cr.dbname).cursor() as cr:
            sp = cr.savepoint()
            sp.__enter__()
            # Kill it the way a database error does.
            with self.assertRaises(psycopg2.Error):
                cr.execute('SELECT 1/0')
            cr.rollback()
            # Must not raise; must report that the savepoint is gone.
            self.assertFalse(
                self.task_ok.with_env(self.env(cr=cr))
                ._close_savepoint_safely(sp))

    def test_close_savepoint_safely_handles_none(self):
        """No savepoint at all is a valid state, not an error."""
        self.assertTrue(self.task_ok._close_savepoint_safely(None))

    def test_tick_continues_after_unclosable_savepoint(self):
        """The blast radius stays one task."""
        poison = self._make_task(
            'Poison chain', 'poison_then_raise', 1, cadence='min')
        after = self._make_task(
            'Runs afterwards', 'succeed', 2, cadence='min')
        self.task_fail.write({'cadence': 'month'})
        self.task_ok.write({'cadence': 'month'})

        result = self.Task._cron_tick('min')

        self.assertEqual(result['failed'], 1)
        self.assertTrue(after.last_run, 'the following task never ran')
        self.assertEqual(poison.failure_count, 1)
