# -*- coding: utf-8 -*-
{
    'name': 'Cron: Tick Engine',
    'version': '18.0.1.0.0',
    'summary': 'Deklarativ schemaläggning — en motor, fem kadenser',
    'category': 'Hidden',
    'author': 'Vertel Sverige AB',
    'website': 'https://vertel.se',
    'license': 'AGPL-3',
    'description': """
        Schemaläggningsmotor för hela ekosystemet.

        Ersätter hundratals enskilda `ir.cron` med EN registreringsmodell
        (`cron.task`) och fem tick-cron — en per kadens:

            min     var 5:e minut
            hour    varje timme
            daily   dagligen (spridd över en timme)
            week    veckovis (spridd över en dag)
            month   månadsvis (spridd över en vecka)

        En modul deklarerar sina uppgifter som data-XML och lägger `cron_tick`
        i `depends`. Motorn känner inte till några uppgifter.

        TRE UTLÖSARTYPER mot samma metod:

          1. Schemalagd  — tick-cron:en kör förfallna uppgifter
          2. Händelsedriven — POST /cron/trigger/<technical_name> (Bearer)
          3. Manuell    — server action + knapp i formuläret

        VARFÖR I ODOO-BASE: cron-schemaläggning är infrastruktur, inte AI.
        Modulen beror ENDAST på `base`, så `odoo-project`, `odoo-saltstack`,
        `odoo-bifrost` och `odoo-keykeep` kan använda den utan att bero på
        AI-stacken. `odoo-project` kan därmed installeras utan `odoo-ai`.

        ISOLERAD FELHANTERING: varje uppgift körs i egen savepoint — en
        kraschande uppgift stoppar inte kedjan.

        ATOMISKT LÅS: sessionsbundet PostgreSQL advisory-lock per uppgift.
        En villkorlig UPDATE räcker INTE — Odoo kör under `repeatable read`,
        där två workers kan båda se låset som tomt och båda skriva.
        `locked_by`/`locked_at` visas i UI:t som information.
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
