# -*- coding: utf-8 -*-
{
    'name': 'Cron: Tick Engine',
    'version': '18.0.2.0.0',
    'summary': 'Declarative scheduling — one engine, five cadences',
    'category': 'Hidden',
    'author': 'Vertel Sverige AB',
    'website': 'https://vertel.se',
    'license': 'AGPL-3',
    'description': """
        Scheduling engine for the entire ecosystem.

        Replaces hundreds of individual `ir.cron` with ONE registry model
        (`cron.task`) and five tick crons — one per cadence:

            min     every 5 minutes
            hour    hourly
            daily   daily (spread over an hour)
            week    weekly (spread over a day)
            month   monthly (spread over a week)

        A module declares its tasks as data XML and adds `cron_tick` to
        `depends`. The engine knows nothing about any task.

        THREE TRIGGER TYPES against the same method:

          1. Scheduled    — the tick cron runs due tasks
          2. Event-driven — POST /cron/trigger/<technical_name> (Bearer)
          3. Manual       — server action + button in the form

        WHY IN ODOO-BASE: cron scheduling is infrastructure, not AI.
        The module depends ONLY on `base`, so `odoo-project`,
        `odoo-saltstack`, `odoo-bifrost` and `odoo-keykeep` can use it
        without depending on the AI stack. `odoo-project` can therefore be
        installed without `odoo-ai`.

        ISOLATED ERROR HANDLING: each task runs in its own savepoint — a
        crashing task does not stop the chain.

        ATOMIC LOCK: session-bound PostgreSQL advisory lock per task.
        A conditional UPDATE is NOT sufficient — Odoo runs under
        `repeatable read`, where two workers can both see the lock as free
        and both write. `locked_by`/`locked_at` are shown in the UI as
        information.
    """,
    'depends': [
        'base',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/config_data.xml',
        'data/cron_tick_data.xml',
        'views/cron_task_views.xml',
    ],
    'demo': [],
    'application': False,
    'installable': True,
    'auto_install': False,
}
