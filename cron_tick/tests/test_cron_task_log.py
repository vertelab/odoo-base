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

from odoo import fields
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

        The creation message (also a note) is excluded by its body, and tests
        run in the admin's language, so assertions never depend on the
        English source strings — they assert on the error text instead.
        """
        return task.message_ids.filtered(
            lambda m: m.message_type == 'notification'
            and m.subtype_id.internal
            and (m.body or '').strip()
            and 'Scheduled Task created' not in (m.body or ''))


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
