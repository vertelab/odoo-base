# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

"""cron.task — deklarativ schemaläggning.

En post per schemalagd uppgift. Moduler deklarerar sina uppgifter som
data-XML; denna modul äger motorn. Motorn känner inte till några uppgifter.

KADENS, INTE INTERVALL
    En uppgift säger *vilken* kadens den tillhör (min/hour/daily/week/month),
    inte ett intervall i sekunder. Därmed försvinner `next_run`-aritmetiken
    per uppgift och hela klassen av beräkningsfel (fel timedelta, fel tidszon,
    glömd next_run vid fel). Bara tick:en behöver veta när den ska köra.

MOTORN ÄGER KÖRHISTORIKEN
    `_run()` rör ALDRIG `last_run`/`failure_count`. Motorn skriver dessa
    efter att uppgiften returnerat eller kastat — en skrivpunkt, inte två.
    Om `_run()` satte `last_run` och sedan kastade skulle savepointen rulla
    tillbaka skrivningen och motorn tro att uppgiften aldrig körts.
"""

import hashlib
import logging
import time
from datetime import datetime, timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

# Kadens → ungefärligt antal sekunder. Används bara för försenad-detektion
# och loggning — INTE för schemaläggning (tick-cron:en äger den).
CADENCE_SECONDS = {
    'min': 300,
    'hour': 3600,
    'daily': 86400,
    'week': 604800,
    'month': 2592000,
}

# Spridningsfönster per kadens (minuter). En `daily`-uppgift sprids över en
# timme, en `week`-uppgift över en dag, en `month`-uppgift över en vecka.
# Utan spridning skulle 19 dygnsjobb alla köra kl 00:00 och skapa en spik av
# tunga batch-operationer samtidigt.
SPREAD_MINUTES = {
    'min': 0,
    'hour': 0,
    'daily': 60,
    'week': 1440,
    'month': 10080,
}


class CronTask(models.Model):
    _name = 'cron.task'
    _description = 'Schemalagd uppgift (cron.task)'
    _order = 'sequence, id'

    # ── Identitet ──────────────────────────────────────────────────────
    name = fields.Char(
        'Namn', required=True,
        help='Läsbart namn som visas i listan.')
    technical_name = fields.Char(
        'Tekniskt namn', required=True, index=True,
        help='Stabil identifierare. Används av händelsedriven triggning '
             '(/cron/trigger/<technical_name>) och för dygnsspridning. '
             'Ändra aldrig på en uppgift som redan är i drift.')
    module = fields.Char(
        'Modul', index=True,
        help='Modulen som äger uppgiften. Vid avinstallation tas XML-posten '
             'bort och uppgiften försvinner.')

    # ── Vad som ska köras ──────────────────────────────────────────────
    model_name = fields.Char(
        'Modell', required=True,
        help='Tekniskt modellnamn, t.ex. "ai.skill". Slås upp vid körning — '
             'därför robust mot moduler som avinstalleras.')
    method_name = fields.Char(
        'Metod', required=True,
        help='Metodnamn på modellen, t.ex. "_sync_from_filesystem". '
             'Anropas utan argument.')

    # ── När ────────────────────────────────────────────────────────────
    cadence = fields.Selection([
        ('min', 'Var 5:e minut'),
        ('hour', 'Varje timme'),
        ('daily', 'Dagligen'),
        ('week', 'Veckovis'),
        ('month', 'Månadsvis'),
    ], string='Kadens', required=True, index=True, default='daily',
        help='Vilken tick-cron som kör uppgiften. Kadensen är ett FÄLT — '
             'ett namnprefix i det tekniska namnet påverkar inte körningen.')
    sequence = fields.Integer(
        'Sekvens', default=10,
        help='Körordning inom kadensen. Lägre värde körs först.')
    active = fields.Boolean('Aktiv', default=True)

    # ── Körning ────────────────────────────────────────────────────────
    timeout_seconds = fields.Integer(
        'Tidsgräns (s)', default=120,
        help='Mjuk tidsgräns. Motorn mäter körtiden och loggar en varning när '
             'gränsen passeras. Python-trådar kan inte avbrytas säkert — '
             'gränsen är därför mätande, inte avbrytande. En uppgift som '
             'konsekvent överskrider gränsen bör flyttas till queue_job.')
    max_failures = fields.Integer(
        'Max fel', default=10,
        help='Antal konsekutiva fel innan uppgiften inaktiveras automatiskt.')

    # ── Körhistorik (ägs av motorn) ────────────────────────────────────
    last_run = fields.Datetime(
        'Senast körd', readonly=True)
    last_duration_ms = fields.Integer(
        'Varaktighet (ms)', readonly=True)
    failure_count = fields.Integer(
        'Fel i följd', readonly=True, default=0)
    last_error = fields.Text(
        'Senaste fel', readonly=True)

    # ── Lås (atomiskt, D10) ────────────────────────────────────────────
    locked_by = fields.Char(
        'Låst av', readonly=True,
        help='Vem som kör uppgiften just nu (t.ex. "tick:min" eller '
             '"webhook"). Tomt = ledig.')
    locked_at = fields.Datetime(
        'Låst sedan', readonly=True)

    # ── Beräknade fält ─────────────────────────────────────────────────
    is_locked = fields.Boolean(
        'Körs nu', compute='_compute_is_locked', search='_search_is_locked')
    is_overdue = fields.Boolean(
        'Försenad', compute='_compute_is_overdue', search='_search_is_overdue',
        help='True när uppgiften inte körts inom tre kadensintervall.')
    cadence_label = fields.Char(
        'Kadens (text)', compute='_compute_cadence_label')

    _sql_constraints = [
        ('technical_name_uniq', 'UNIQUE(technical_name)',
         'Det tekniska namnet måste vara unikt — det är uppgiftens identitet.'),
    ]

    # ───────────────────────────────────────────────────────────────────
    # Beräknade fält
    # ───────────────────────────────────────────────────────────────────

    @api.depends('locked_by')
    def _compute_is_locked(self):
        for task in self:
            task.is_locked = bool(task.locked_by)

    @api.depends('last_run', 'cadence', 'active')
    def _compute_is_overdue(self):
        now = fields.Datetime.now()
        for task in self:
            if not task.active or not task.last_run:
                task.is_overdue = False
                continue
            limit = CADENCE_SECONDS.get(task.cadence, 86400) * 3
            task.is_overdue = (now - task.last_run).total_seconds() > limit

    @api.depends('cadence')
    def _compute_cadence_label(self):
        labels = dict(self._fields['cadence'].selection)
        for task in self:
            task.cadence_label = labels.get(task.cadence, task.cadence or '')

    def _search_is_locked(self, operator, value):
        """Sökbar motsvarighet till `is_locked` (locked_by är satt)."""
        if operator in ('=', '!=') and isinstance(value, bool):
            # is_locked = True  → locked_by != False
            # is_locked = False → locked_by = False
            if (operator == '=' and value) or (operator == '!=' and not value):
                return [('locked_by', '!=', False)]
            return [('locked_by', '=', False)]
        return [('locked_by', operator, value)]

    def _search_is_overdue(self, operator, value):
        """Sökbar motsvarighet till `is_overdue`.

        Försenad = aktiv, har körts, och senaste körning är äldre än tre
        kadensintervall. Tröskeln beror på kadensen, så vi bygger ett OR
        över kadenserna.

        ⚠ `['!'] + ['|']*N + terms` negerar INTE hela OR-gruppen i Odoos
        prefix-notation — det ger en domän som varken matchar sant eller
        falskt. Vi negerar därför varje term för sig.
        """
        now = fields.Datetime.now()
        if operator not in ('=', '!='):
            return []
        want = value if operator == '=' else not value

        # En OR-gren per kadens: (cadence = X AND last_run < tröskel)
        branches = []
        for cadence, seconds in CADENCE_SECONDS.items():
            limit = now - timedelta(seconds=seconds * 3)
            branches.append([
                ('cadence', '=', cadence),
                ('last_run', '!=', False),
                ('last_run', '<', limit),
            ])

        # ⚠ Odoo 18 vill ha en PLATT domän i prefix-notation — nestlade
        # listor kraschar i `domain_combine_anies`.
        #
        # ⚠⚠ Prefix-notation kräver ett operator-TEKEN per sammanfogning:
        # en grupp med 3 operander behöver '&','&' (inte ett enda '&' —
        # då binder operatorn fel och domänen matchar ingenting).
        # Samma gäller OR-kedjan: N grenar kräver N-1 inledande '|'.
        def _and_group(branch):
            return ['&'] * (len(branch) - 1) + list(branch)

        if want:
            or_ops = ['|'] * (len(branches) - 1)
            return or_ops + [t for b in branches for t in _and_group(b)]

        # NOT(OR över grenar) — negera varje gren för sig och AND:a dem.
        # NOT(a OR b) == (NOT a) AND (NOT b)
        negated = [['!'] + _and_group(b) for b in branches]
        and_ops = ['&'] * (len(negated) - 1)
        return and_ops + [t for g in negated for t in g]

    # ───────────────────────────────────────────────────────────────────
    # Spridning (D7)
    # ───────────────────────────────────────────────────────────────────

    def _spread_offset_minutes(self):
        """Deterministisk spridning inom kadensens fönster.

        Samma tekniska namn ger samma offset varje gång — en `daily`-uppgift
        körs alltså vid samma klockslag varje dag, inte slumpmässigt.
        """
        self.ensure_one()
        window = SPREAD_MINUTES.get(self.cadence, 0)
        if not window:
            return 0
        digest = hashlib.sha256(
            (self.technical_name or '').encode('utf-8')).hexdigest()
        return int(digest, 16) % window

    # ───────────────────────────────────────────────────────────────────
    # Kadenslogik (D7)
    # ───────────────────────────────────────────────────────────────────

    def _is_due(self, now=None):
        """Är uppgiften förfallen i sin kadens?

        `min`/`hour` styrs av tidsgränsen sedan senaste körning.
        `daily`/`week`/`month` styrs av spridningsfönstret — uppgiften körs
        när fönstret öppnat och den inte redan körts i perioden.
        """
        self.ensure_one()
        now = now or fields.Datetime.now()

        if self.cadence == 'min':
            return True

        if self.cadence == 'hour':
            if not self.last_run:
                return True
            return (now - self.last_run).total_seconds() >= 3600

        # daily / week / month — spridning över ett fönster.
        offset = self._spread_offset_minutes()
        if self.cadence == 'daily':
            # Fönstret är en timme: kör när minut >= offset och inte körts idag.
            if not self.last_run:
                return now.minute >= offset
            return self.last_run.date() < now.date() and now.minute >= offset

        if self.cadence == 'week':
            # Fönstret är en dag (1440 min): offset i minuter sedan midnatt.
            window_open = now.hour * 60 + now.minute >= offset
            if not self.last_run:
                return window_open
            return (now - self.last_run).days >= 7 and window_open

        if self.cadence == 'month':
            # Fönstret är en vecka (10080 min): offset i minuter sedan
            # veckans start (måndag 00:00).
            minutes_into_week = now.weekday() * 1440 + now.hour * 60 + now.minute
            window_open = minutes_into_week >= offset
            if not self.last_run:
                return window_open
            return (now - self.last_run).days >= 28 and window_open

        return False

    # ───────────────────────────────────────────────────────────────────
    # Körning — den enda körvägen (D9, D12)
    # ───────────────────────────────────────────────────────────────────

    def _run(self):
        """Kör uppgiften. REN metod — rör aldrig körhistoriken.

        Returnerar metodens resultat. Kastar vidare fel till anroparen, som
        bokför dem. Motorn (och webhook/manuell) äger `last_run`,
        `last_duration_ms` och `failure_count`.
        """
        self.ensure_one()
        model = self.env.get(self.model_name)
        if model is None:
            raise UserError(_(
                'Modellen "%s" finns inte (uppgift %s). Modulen kan vara '
                'avinstallerad.') % (self.model_name, self.technical_name))
        method = getattr(model, self.method_name, None)
        if method is None or not callable(method):
            raise UserError(_(
                'Metoden "%s" finns inte på modellen "%s" (uppgift %s).'
            ) % (self.method_name, self.model_name, self.technical_name))
        return method()

    def _execute(self, owner='manual'):
        """Kör uppgiften med lås, mätning och bokföring.

        Detta är den gemensamma vägen för alla tre utlösartyper. Returnerar
        en dict med status och varaktighet.
        """
        self.ensure_one()
        if not self._acquire_lock(owner):
            return {
                'status': 'locked',
                'technical_name': self.technical_name,
            }
        started = time.monotonic()
        try:
            try:
                with self.env.cr.savepoint():
                    self._run()
            except Exception as exc:  # noqa: BLE001 — motorn fångar allt
                duration_ms = int((time.monotonic() - started) * 1000)
                self.env.invalidate_all()
                self.browse(self.id)._record_failure(exc, duration_ms)
                _logger.exception(
                    'cron.task %s misslyckades (%s ms)',
                    self.technical_name, duration_ms)
                return {
                    'status': 'error',
                    'technical_name': self.technical_name,
                    'duration_ms': duration_ms,
                    'error': str(exc),
                }
            duration_ms = int((time.monotonic() - started) * 1000)
            self.env.invalidate_all()
            task = self.browse(self.id)
            task._record_success(duration_ms)
            if duration_ms > self.timeout_seconds * 1000:
                _logger.warning(
                    'cron.task %s överskred tidsgränsen: %s ms > %s s',
                    self.technical_name, duration_ms, self.timeout_seconds)
            return {
                'status': 'ok',
                'technical_name': self.technical_name,
                'duration_ms': duration_ms,
            }
        finally:
            # Släpp advisory-låset ÄVEN vid fel — annars hålls det till
            # anslutningen stängs och uppgiften kan aldrig köras igen.
            self.browse(self.id)._release_lock()

    # ───────────────────────────────────────────────────────────────────
    # Lås (D10 — atomiskt via advisory-lock, oberoende av isolationsnivå)
    # ───────────────────────────────────────────────────────────────────

    def _acquire_lock(self, owner):
        """Ta låset atomiskt. Returnerar True om vi fick det.

        ⚠ En villkorlig UPDATE är INTE tillräcklig: Odoo kör under
        `repeatable read`, och två transaktioner kan båda se `locked_by`
        som tomt i sin snapshot och båda få `rowcount == 1`. Verifierat i
        drift — två samtidiga workers körde samma uppgift.

        Vi använder i stället ett sessionsbundet advisory-lock per uppgift
        (`pg_try_advisory_lock`), som är atomiskt oavsett isolationsnivå.
        `locked_by`/`locked_at` skrivs som INFORMATION (vem kör), inte som
        själva låset — det senare ägs av PostgreSQL.

        Låset släpps av `_release_lock()` eller automatiskt när sessionen
        (anslutningen) stängs.
        """
        self.ensure_one()
        lock_id = self._task_lock_id()
        self.env.cr.execute('SELECT pg_try_advisory_lock(%s)', (lock_id,))
        row = self.env.cr.fetchone()
        if not row or not row[0]:
            return False
        # Vi äger låset. Skriv information om vem som kör.
        self.env.cr.execute("""
            UPDATE cron_task
               SET locked_by = %s, locked_at = now()
             WHERE id = %s
        """, (owner, self.id))
        self.env.invalidate_all()
        return True

    def _release_lock(self):
        """Frigör låset efter körning."""
        self.ensure_one()
        lock_id = self._task_lock_id()
        self.env.cr.execute('SELECT pg_advisory_unlock(%s)', (lock_id,))
        self.env.cr.execute("""
            UPDATE cron_task
               SET locked_by = NULL, locked_at = NULL
             WHERE id = %s
        """, (self.id,))
        self.env.invalidate_all()

    def _task_lock_id(self):
        """Stabilt advisory-lock-id per uppgift (ryms i int8).

        Ett eget namnrymdsprefix håller uppgiftslåsen åtskilda från
        kadenslåsen i `_advisory_lock_id`.
        """
        self.ensure_one()
        digest = hashlib.sha256(
            ('cron_task:lock:%s' % self.technical_name).encode('utf-8')
        ).hexdigest()
        return int(digest, 16) % (2 ** 31)

    # ───────────────────────────────────────────────────────────────────
    # Bokföring (D8, D9)
    # ───────────────────────────────────────────────────────────────────

    def _record_success(self, duration_ms):
        """Bokför lyckad körning. Nollställer felräknaren."""
        self.ensure_one()
        self.write({
            'last_run': fields.Datetime.now(),
            'last_duration_ms': duration_ms,
            'failure_count': 0,
            'last_error': False,
            'locked_by': False,
            'locked_at': False,
        })

    def _record_failure(self, exc, duration_ms=0):
        """Bokför misslyckad körning. Inaktiverar efter `max_failures`.

        ⚠ Anropas EFTER att savepointen rullats tillbaka — anroparen måste
        ha kört `invalidate_all()` och hämtat posten på nytt, annars skriver
        vi till en post vars transaktion är borta.
        """
        self.ensure_one()
        count = self.failure_count + 1
        vals = {
            'last_run': fields.Datetime.now(),
            'last_duration_ms': duration_ms,
            'failure_count': count,
            'last_error': str(exc)[:4000],
            'locked_by': False,
            'locked_at': False,
        }
        if count >= self.max_failures:
            vals['active'] = False
            _logger.error(
                'cron.task %s inaktiverad efter %s fel i följd',
                self.technical_name, count)
        self.write(vals)

    # ───────────────────────────────────────────────────────────────────
    # Motorn (D6, D8, D11)
    # ───────────────────────────────────────────────────────────────────

    @api.model
    def _cron_tick(self, cadence):
        """Kör alla förfallna uppgifter i en kadens.

        Skyddad av ett globalt advisory-lock per kadens (D11) så att två
        Odoo-workers inte kör samma kadens samtidigt.
        """
        lock_id = self._advisory_lock_id(cadence)
        self.env.cr.execute(
            'SELECT pg_try_advisory_lock(%s)', (lock_id,))
        got_lock = self.env.cr.fetchone()
        if not got_lock or not got_lock[0]:
            _logger.info(
                'cron.tick %s: en annan worker kör redan — hoppar över',
                cadence)
            return {'cadence': cadence, 'skipped': 'locked'}

        try:
            now = fields.Datetime.now()
            candidates = self.search([
                ('active', '=', True),
                ('cadence', '=', cadence),
            ], order='sequence, id')
            due = candidates.filtered(lambda t: t._is_due(now))

            ran, failed, locked = 0, 0, 0
            for task in due:
                task_id = task.id
                if not task._acquire_lock('tick:%s' % cadence):
                    locked += 1
                    continue
                started = time.monotonic()
                try:
                    try:
                        with self.env.cr.savepoint():
                            task._run()
                    except Exception as exc:  # noqa: BLE001
                        duration_ms = int((time.monotonic() - started) * 1000)
                        # Savepointen rullades tillbaka — ORM-cachen är
                        # korrupt. Hämta posten på nytt innan felet skrivs
                        # (D8).
                        self.env.invalidate_all()
                        self.browse(task_id)._record_failure(exc, duration_ms)
                        _logger.exception(
                            'cron.task %s misslyckades i tick %s',
                            task.technical_name, cadence)
                        failed += 1
                        continue
                    duration_ms = int((time.monotonic() - started) * 1000)
                    self.env.invalidate_all()
                    self.browse(task_id)._record_success(duration_ms)
                    if duration_ms > task.timeout_seconds * 1000:
                        _logger.warning(
                            'cron.task %s överskred tidsgränsen: %s ms > %s s',
                            task.technical_name, duration_ms,
                            task.timeout_seconds)
                    ran += 1
                finally:
                    # Släpp uppgiftslåset i varje varv — annars hålls det
                    # till anslutningen stängs och uppgiften blockeras.
                    self.browse(task_id)._release_lock()

            _logger.info(
                'cron.tick %s: %s körda, %s misslyckade, %s låsta',
                cadence, ran, failed, locked)
            return {
                'cadence': cadence,
                'ran': ran,
                'failed': failed,
                'locked': locked,
            }
        finally:
            self.env.cr.execute(
                'SELECT pg_advisory_unlock(%s)', (lock_id,))

    @api.model
    def _advisory_lock_id(self, cadence):
        """Stabilt advisory-lock-id per kadens (ryms i int4)."""
        digest = hashlib.sha256(
            ('cron_tick:%s' % cadence).encode('utf-8')).hexdigest()
        return int(digest, 16) % (2 ** 31)

    # ───────────────────────────────────────────────────────────────────
    # Manuell körning (D12)
    # ───────────────────────────────────────────────────────────────────

    def action_run_now(self):
        """Kör uppgiften omedelbart — manuell utlösare.

        Respekterar låset: en uppgift som redan körs nekas med ett tydligt
        meddelande i stället för att köras dubbelt.
        """
        self.ensure_one()
        result = self._execute(owner='manual')
        if result['status'] == 'locked':
            raise UserError(_(
                'Uppgiften "%s" körs redan (%s). Försök igen när den är klar.'
            ) % (self.name, self.locked_by or 'okänd'))
        if result['status'] == 'error':
            raise UserError(_(
                'Uppgiften "%s" misslyckades:\n%s'
            ) % (self.name, result.get('error', '')))
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Uppgift körd'),
                'message': _(
                    '%s kördes på %s ms.') % (
                    self.name, result.get('duration_ms', 0)),
                'type': 'success',
                'sticky': False,
            },
        }

    # ───────────────────────────────────────────────────────────────────
    # Hjälp för webhook (D12)
    # ───────────────────────────────────────────────────────────────────

    @api.model
    def _find_by_technical_name(self, technical_name):
        """Slå upp en uppgift på tekniskt namn. Tom recordset om ingen."""
        return self.search([
            ('technical_name', '=', technical_name),
        ], limit=1)
