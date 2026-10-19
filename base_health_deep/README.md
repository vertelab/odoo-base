# Base: Deep Health Check

Registry-aware health endpoint for load balancers and monitoring.

## Why this module exists

Odoo core ships `/web/health` (`odoo/addons/web/controllers/home.py`). It
returns `{"status": "pass"}` without touching the registry or the database.
The only optional check is `?db_server_status=1`, which opens a raw cursor —
it still never asks the registry for anything.

On 2026-10-19 `base_dav` failed to import because it whitelisted a `vobject`
attribute that does not exist (`vCalendar`; vobject 0.9.9 exports `iCalendar`).
The registry could not be built, every HTTP worker entered a crash/respawn
loop and `/web/login` answered `302 -> /web/login` indefinitely.
`/web/health` returned `pass` for the entire outage, so monitoring saw a
healthy instance while the ERP was unusable.

This module adds an endpoint that fails the way the instance actually fails.

## Endpoint

    GET /health/deep            → JSON
    GET /health/deep?format=text → "OK" or "FAIL: <reason>"

Healthy response (HTTP 200):

```json
{
  "status": "pass",
  "checks": {
    "registry": true,
    "database": true,
    "base_module": true,
    "workers": 9
  },
  "db_latency_ms": 0.22,
  "cron_failures": 4,
  "duration_ms": 4.63,
  "database_name": "ledningssystem"
}
```

Unhealthy response (HTTP 503) adds `errors` with the failed checks.

| Check | Meaning |
|---|---|
| `registry` | `request.env.registry.ready` — false when loaded but not set up |
| `database` | round-trip of `SELECT 1` through the ORM cursor |
| `base_module` | core models (`ir.module.module`, `res.users`, `res.partner`) are registered |
| `workers` | odoo processes sharing this worker's cmdline (informational) |
| `cron_failures` | active `ir.cron` jobs with `failure_count > 0` (informational) |

The route uses `request.env`, so it **inherits registry breakage**. That is
deliberate: if the registry cannot be built, this endpoint cannot answer
either, and the probe fails — instead of lying like `/web/health` does.

## Verified behaviour

Reproduced on a throwaway database (2026-10-19) with an installed module
whose import raises `AttributeError: module 'vobject' has no attribute
'vCalendar'` — the exact production failure:

| Endpoint | Result during the outage |
|---|---|
| `/web/health` | `{"status": "pass"}` — HTTP 200, false negative |
| `/health/deep` | no valid response (registry unusable) |
| `/web/login` | redirect loop / HTML, not 200 |

## Configuration

Nothing to configure. `auth="none"`, `save_session=False`, and the route is
read-only apart from `SELECT 1`.

If the endpoint is reachable from untrusted networks, note that it exposes
the database name and the number of cron failures. Restrict it at the proxy
if that matters.

## Maintainer

Vertel Sverige AB.
