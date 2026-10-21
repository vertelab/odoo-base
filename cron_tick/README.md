# cron_tick — declarative scheduling

One engine, five cadences, one registry model. Replaces hundreds of
individual `ir.cron` with `cron.task`.

## The problem

Every `ir.cron` carries its own scheduling: `interval_number`,
`interval_type`, `nextcall`. That produces three classes of errors:

1. **Arithmetic.** Every task computes its own next run. Wrong `timedelta`,
   wrong timezone, forgotten `nextcall` on failure.
2. **Spikes.** 64 of 135 crons ran daily — most of them around midnight.
3. **Opacity.** `ai_agent_core` had 27 of its own `ir.cron` in one flat
   list, with no link to the code that owns them.

## The solution

A module declares its tasks as data XML and adds `cron_tick` to `depends`.
The engine knows nothing about any task.

```xml
<record id="cron_skill_sync" model="cron.task">
    <field name="name">Pi: sync skills</field>
    <field name="technical_name">skill_sync</field>
    <field name="model_name">ai.skill</field>
    <field name="method_name">_sync_from_filesystem</field>
    <field name="cadence">daily</field>
    <field name="module">ai_agent_core</field>
</record>
```

The engine runs it via `cron_daily`. No `nextcall`, no arithmetic.

## The five cadences

| Cadence | Tick cron     | Spread                              |
|---------|---------------|-------------------------------------|
| `min`   | every 5 min   | none — runs every time              |
| `hour`  | hourly        | none — runs when > 1 h since last   |
| `daily` | once a day    | over an hour (`hash % 60`)          |
| `week`  | once a week   | over a day (`hash % 1440`)          |
| `month` | once a month  | over a week (`hash % 10080`)        |

The spread is **deterministic**: `sha256(technical_name) % window`. The same
task runs at the same time each period — not randomly — but different tasks
are spread across the window so they do not collide.

**Why 5 minutes and not 1:** `_heartbeat_all` and friends already have an
internal 5-minute check. When the cron ran every minute, 4 of 5 wakeups were
guaranteed waste.

## Custom intervals

The five cadences cannot express every interval. The original `ir.cron` set
included 15 minutes, 6 hours and 14 days — mapping those onto the nearest
cadence would have changed behaviour (15 min → `min` is 3x more often,
6 h → `hour` is 6x, 14 days → `month` is 14x).

A task may therefore set an interval instead of a cadence:

```xml
<record id="cron_usage_snapshots" model="cron.task">
    <field name="name">Bifrost: usage snapshots</field>
    <field name="technical_name">bifrost_usage_snapshots</field>
    <field name="model_name">bifrost.usage.snapshot</field>
    <field name="method_name">cron_snapshots</field>
    <field name="interval_number">15</field>
    <field name="interval_type">minutes</field>
    <field name="module">bifrost</field>
</record>
```

Rules:

- **Cadence XOR interval.** A task sets one of them, never both and never
  neither. Enforced in Python (`_check_schedule` + `create`) so the message
  is readable.
- **The `min` tick carries interval tasks.** They are checked every 5
  minutes and run when their own interval has elapsed, so the granularity
  matches `ir.cron`. No sixth tick cron.
- **Measured from `last_run`.** A slow run does not drift the schedule —
  the next run is N units after the previous one *finished*.
- **No spreading.** The interval is its own spacing. Tasks with the same
  interval and a common start (e.g. after a deploy) may cluster; that is
  accepted for the few tasks that need a custom interval.

`interval_type` accepts `minutes`, `hours`, `days`, `weeks`, `months`.
Months are 30 days, the same approximation as the cadences.

## Three trigger types — one run path

```
Salt deploy ──┐
Webhook ──────┤──► cron.task._run()
Manual button ┤
Tick ─────────┘
```

### 1. Scheduled

The tick cron calls `model._cron_tick('<cadence>')`. It fetches active tasks
in the cadence, filters on `_is_due()`, sorts by `sequence, id` and runs each
one.

### 2. Event-driven (webhook)

```bash
curl -X POST https://<host>/cron/trigger/skill_sync \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"call","params":{}}'
```

Always responds **HTTP 200** — a sender that receives 4xx/5xx retries
forever, and the trigger is not idempotent (the task runs).

| Situation        | Response                                       |
|------------------|------------------------------------------------|
| disabled         | `{"status": "disabled"}`                       |
| wrong/missing token | `{"status": "error", "error": "Unauthorized"}` |
| unknown name     | `{"status": "not_found", ...}`                 |
| run ok           | `{"status": "ok", "duration_ms": 3}`           |
| run failed       | `{"status": "error", "error": "..."}`          |

Token: `cron_tick.webhook_token`, falling back to
`saltstack.alert.webhook_token` — Salt minions therefore do not need a second
key. Disable with `cron_tick.webhook_enabled = False`.

### 3. Manual

The **Run now** button in the form (`action_run_now`). Refuses if the task is
running.

## Execution — the engine owns the history

`_run()` is **pure**: it resolves the model, calls the method, returns the
result. It never touches `last_run`, `failure_count` or `last_error`.

The engine records after the run. **One write point, not two.** If `_run()`
set `last_run` and then raised, the savepoint would roll back the write and
the engine would believe the task never ran.

All three triggers go through **one** method, `_run_locked_task()`:

```
lock → savepoint → _run() → _record_success/_record_failure → _log_run_record
```

`_cron_tick()` and `_execute()` only differ in what they pass as
`trigger`/`trigger_detail`, so the tick path and the webhook path cannot
drift apart. Their return values are unchanged (`{'cadence','ran','failed',
'locked'}` and `{'status',...}`) — the webhook contract is intact.

## Run log — `cron.task.log`

`cron.task` keeps only the **latest** run. `last_error` is overwritten by the
next success, so an error survives only until the task happens to work again.
The run log keeps every run.

| Field            | Description                                              |
|------------------|----------------------------------------------------------|
| `task_id`        | The task (cascade delete)                                |
| `task_name`, `technical_name`, `module` | Snapshot — readable after a rename |
| `run_at`         | When the run started (indexed)                           |
| `status`         | `ok` / `error` / `locked` / `skipped`                    |
| `trigger`        | `tick` / `webhook` / `manual`                            |
| `trigger_detail` | Cadence for a tick, user name for a manual run           |
| `user_id`        | Who pressed "Run now" (manual only)                      |
| `duration_ms`    | Measured run time (0 for locked/skipped)                 |
| `text`           | Short description; the error message for a failure       |

**Order:** `_order = 'run_at desc, id desc'` — newest first, in the list view
and in the smart button's list. The view sets no `default_order`, so it cannot
drift from the model.

**Colour:** the list is decorated — red on `error`, orange on `locked`, muted
on `skipped`.

**Why a dedicated model and not `mail.message`:** the `min` tick can produce
thousands of rows a day. `mail.message` cannot be filtered on status,
aggregated per task, or pruned per task.

**Why the log is written in `_record_*` and not in `_run()`:** if the log were
written inside `_run()` and the method then raised, the savepoint would roll
back the write and the log would vanish exactly when it is needed. The log
write is also wrapped in `try/except` — history must never be the reason a run
is reported as failed.

### Retention

`cron_tick.log_retention_days` (system parameter, **default 90**). Enforced by
the `cron_log_cleanup` task (cadence `daily`), which calls
`cron.task.log._cron_cleanup()` and deletes in batches.

- `0` (or less) **disables** cleanup — that is the rollback switch.
- An unparsable value falls back to 90 with a warning in the log.

## Chatter

`cron.task` inherits `mail.thread` + `mail.activity.mixin`.

- **Tracked fields:** `active` and `cadence` only. Not `last_run` — a message
  per run would bury everything else.
- **Explicit messages** (`mail.mt_note`) on three events only:
  1. auto-deactivation after `max_failures`,
  2. the **first** failure in a new streak (`failure_count` was 0),
  3. manual re-activation of a deactivated task.
- Repeating failures in the same streak produce a run log record but **no**
  new message.
- Every `message_post` is wrapped in `try/except`: chatter must never change
  the outcome of a run.

**Smart button:** *Runs* in the form (`run_log_count`, computed with one
`read_group`) opens the log filtered on the task.

## Menu

*Technical → Cron Runs* (`base.menu_custom`, sequence 96).

## Error isolation

Each task runs in its own savepoint:

```python
try:
    with self.env.cr.savepoint():
        task._run()
except Exception as exc:
    self.env.invalidate_all()          # ORM cache is corrupt after rollback
    self.browse(task_id)._record_failure(exc, duration_ms)
```

WARNING: `invalidate_all()` + `browse()` is **mandatory**. After a rollback
the ORM cache points at data that does not exist in the database — writing to
that record gives `could not serialize access due to concurrent update`.

After `max_failures` consecutive failures the task is deactivated
automatically.

## Locking

Per task: **session-bound PostgreSQL advisory lock**.

```python
lock_id = sha256(f'cron_task:lock:{technical_name}') % 2**31
self.env.cr.execute('SELECT pg_try_advisory_lock(%s)', (lock_id,))
```

WARNING: **a conditional UPDATE is not sufficient.** Odoo runs under
`repeatable read`. Two transactions can both see `locked_by` as empty in
their snapshot and both get `rowcount == 1`. Verified in production — two
concurrent processes ran the same task. The advisory lock is atomic
regardless of isolation level.

`locked_by`/`locked_at` remain as **information** (who is running, since
when) — not as the lock itself.

WARNING: advisory locks are **re-entrant within the same session**. Two
`_acquire_lock` calls on the same connection both return `True`. That is
documented behaviour — but it means a test in a single `odoo shell` session
cannot prove mutual exclusion. Use two real connections.

WARNING: the lock is released in `finally`. Without it, it is held until the
connection closes (which can be hours in a worker) and the task can never run
again.

Per cadence: a global `pg_try_advisory_lock` in `_cron_tick`, so two workers
do not run the same cadence simultaneously.

## Fields

| Field              | Description                                          |
|--------------------|------------------------------------------------------|
| `name`             | Readable name                                        |
| `technical_name`   | Stable identifier (unique) — used by webhook + spread |
| `module`           | The module that owns the task                        |
| `model_name`       | Technical model name (string, not FK)                |
| `method_name`      | Method name — called without arguments               |
| `cadence`          | `min`/`hour`/`daily`/`week`/`month`                  |
| `sequence`         | Run order within the cadence                         |
| `timeout_seconds`  | Soft time limit (measuring, not aborting)            |
| `max_failures`     | Consecutive failures before auto-deactivation        |
| `last_run`         | Last run (owned by the engine)                       |
| `last_duration_ms` | Duration (owned by the engine)                       |
| `failure_count`    | Consecutive failures (owned by the engine)           |
| `last_error`       | Latest error message                                 |
| `locked_by`        | Who is running (information)                         |
| `locked_at`        | Since when (information)                             |

`model_name`/`method_name` are **strings**, not an `ir.model` FK. That makes
the task robust at `--update`: a module that is uninstalled produces a clear
error message instead of a crashing FK.

## The time limit is soft

Python threads cannot be aborted safely. `timeout_seconds` **measures** and
logs a warning — it does not abort. A task that consistently exceeds the
limit should be moved to `queue_job`.

## The cadence is a field, not a name prefix

A name prefix (`daily_...`) cannot be trusted — someone renames it and the
schedule changes silently. The `cadence` field is the truth.

## Installation

```bash
checkmodule -d <db> -m cron_tick
```

The module depends **only on `base`**. `odoo-project`, `odoo-saltstack`,
`odoo-bifrost` and `odoo-keykeep` can use it without depending on the AI
stack — `odoo-project` can be installed without `odoo-ai`.

## Migrating an existing `ir.cron`

1. Add the task as `cron.task` in the module's data XML.
2. Set the old `ir.cron` to `active = False` and prefix the name with
   `[MIGRATED -> cron.task]`.
3. Do **not** delete — keep it for a month for comparison.
4. Verify in production before cleanup.

## Troubleshooting

| Symptom | Likely cause |
|---------|--------------|
| The task never runs | `active=False` (auto-deactivated after `max_failures`?) — see `last_error` |
| `The model "X" does not exist` | The module is uninstalled, or `model_name` is misspelled |
| `The method "X" does not exist` | Wrong method name, or the module was upgraded |
| The task appears to hang | `locked_by` is set — a worker is running. Check `locked_at` |
| `could not serialize access` | Write after rollback without `invalidate_all()` |
| `search` on `is_overdue` returns 0 | Wrong prefix domain — see `_search_is_overdue` |
