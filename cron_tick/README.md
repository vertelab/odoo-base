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

The engine (`_cron_tick`, `_execute`) records after the run. **One write
point, not two.** If `_run()` set `last_run` and then raised, the savepoint
would roll back the write and the engine would believe the task never ran.

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
