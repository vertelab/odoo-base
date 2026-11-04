# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
"""Registry-aware health endpoint.

Odoo core ships ``/web/health`` (``odoo/addons/web/controllers/home.py``).
It answers ``{"status": "pass"}`` without touching the registry or the
database unless ``?db_server_status=1`` is passed, and even then it only
opens a raw cursor -- it never asks the registry for anything.

That is not enough.  On 2026-10-19 a module (``base_dav``) failed to import
because it whitelisted a ``vobject`` attribute that does not exist.  The
registry could not be built, every HTTP worker entered a crash/respawn loop
and ``/web/login`` answered ``302 -> /web/login`` forever.  ``/web/health``
kept returning ``pass`` throughout, so monitoring saw a healthy instance
during a total outage.

This controller exists so a probe can fail the way the instance actually
fails.  It goes through ``request.env`` and therefore inherits registry
breakage: if the registry is unusable, this route cannot answer either.

Checks (each independently reported):

``registry``
    ``request.env.registry.ready`` -- false when the registry is loaded but
    not ready, e.g. during a failed update.
``database``
    round-trip time of ``SELECT 1`` through the ORM cursor.
``base_module``
    ``base`` is present in the registry's module graph.  A registry that
    exists but lost its base module cannot serve anything.
``cron``
    number of active ``ir.cron`` jobs whose last run failed.  Not an error
    by itself (jobs retry), but reported so a burn-rate alert can use it.
``workers``
    number of odoo processes, read from the process table.  Informational.

Default response is JSON.  ``?format=text`` returns ``OK``/``FAIL`` plus a
one-line reason, which is friendlier for ``curl`` in shell probes.
"""
import json
import os
import time

from odoo import http
from odoo.http import request


def _count_odoo_processes():
    """Count processes running the same odoo executable as this worker.

    Odoo 18 does not put ``--http`` on the worker cmdline (that was <= 17),
    so every worker shares the master's command line.  Counting via /proc is
    dependency-free and works inside containers.
    """
    try:
        with open("/proc/%d/cmdline" % os.getpid(), "rb") as fh:
            own = fh.read().split(b"\0")
        # Identify the interpreter+script pair, e.g. ['/usr/bin/python3',
        # '/usr/bin/odoo'] so we do not count unrelated python processes.
        own_head = b" ".join([p for p in own[:2] if p])
        count = 0
        for pid in os.listdir("/proc"):
            if not pid.isdigit():
                continue
            try:
                with open("/proc/%s/cmdline" % pid, "rb") as fh:
                    cmd = b" ".join([p for p in fh.read().split(b"\0")[:2] if p])
            except (IOError, OSError):
                continue
            if cmd == own_head:
                count += 1
        return count
    except (IOError, OSError):
        return 0


class DeepHealth(http.Controller):
    @http.route("/health/deep", type="http", auth="none", save_session=False)
    def deep_health(self, format="json", **kwargs):  # noqa: A002
        started = time.monotonic()
        checks = {}
        errors = []

        # -- registry -------------------------------------------------
        # Reaching this line at all means a controller was dispatched, which
        # already implies a registry instance exists.  ``ready`` catches the
        # loaded-but-not-ready state.
        registry = getattr(request.env, "registry", None)
        registry_ready = bool(registry is not None and registry.ready)
        checks["registry"] = registry_ready
        if not registry_ready:
            errors.append("registry not ready")

        # -- database -------------------------------------------------
        db_ms = None
        try:
            t0 = time.monotonic()
            request.env.cr.execute("SELECT 1")
            request.env.cr.fetchone()
            db_ms = round((time.monotonic() - t0) * 1000.0, 2)
            checks["database"] = True
        except Exception as exc:  # noqa: BLE001 - report, never raise
            checks["database"] = False
            errors.append("database: %s" % type(exc).__name__)

        # -- base module present in the registry ----------------------
        # ``registry.ready`` only says setup finished; it does not say the
        # module graph is intact.  Test that a handful of core models that
        # ``base`` itself defines are actually registered.  Checking the ORM
        # (not just a name list) is deliberate: if these are missing, nothing
        # else in the registry can work either.
        base_ok = False
        try:
            models = request.env.registry.models
            base_ok = all(
                name in models
                for name in ("ir.module.module", "res.users", "res.partner")
            )
        except Exception:  # noqa: BLE001 - report, never raise
            base_ok = False
        checks["base_module"] = base_ok
        if not base_ok:
            errors.append("core models missing from registry")

        # -- cron failures (informational) ----------------------------
        cron_failed = None
        try:
            request.env.cr.execute(
                "SELECT count(*) FROM ir_cron WHERE active IS TRUE "
                "AND failure_count > 0"
            )
            cron_failed = request.env.cr.fetchone()[0]
        except Exception:  # noqa: BLE001 - table may be absent on bare db
            cron_failed = None

        checks["workers"] = _count_odoo_processes()

        healthy = all([
            checks["registry"],
            checks["database"],
            checks["base_module"],
        ])

        payload = {
            "status": "pass" if healthy else "fail",
            "checks": checks,
            "db_latency_ms": db_ms,
            "cron_failures": cron_failed,
            "duration_ms": round((time.monotonic() - started) * 1000.0, 2),
            "database_name": request.db,
        }
        if errors:
            payload["errors"] = errors

        status = 200 if healthy else 503

        if format == "text":
            body = "OK" if healthy else "FAIL: %s" % "; ".join(errors)
            return request.make_response(
                body + "\n",
                [("Content-Type", "text/plain; charset=utf-8"),
                 ("Cache-Control", "no-store")],
                status=status,
            )

        return request.make_response(
            json.dumps(payload),
            [("Content-Type", "application/json"),
             ("Cache-Control", "no-store")],
            status=status,
        )
