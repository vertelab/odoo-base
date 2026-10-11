# cron_tick — deklarativ schemaläggning

En motor, fem kadenser, en registreringsmodell. Ersätter hundratals enskilda
`ir.cron` med `cron.task`.

## Problemet

Varje `ir.cron` bär sin egen schemaläggning: `interval_number`,
`interval_type`, `nextcall`. Det ger tre klasser av fel:

1. **Aritmetik.** Varje uppgift räknar sin egen nästa körning. Fel
   `timedelta`, fel tidszon, glömd `nextcall` vid fel.
2. **Spikar.** 64 av 135 cron körde dagligen — de flesta kring midnatt.
3. **Oöverskådlighet.** `ai_agent_core` hade 27 egna `ir.cron` i en platt
   lista, utan koppling till koden som äger dem.

## Lösningen

En modul deklarerar sina uppgifter som data-XML och lägger `cron_tick` i
`depends`. Motorn känner inte till några uppgifter.

```xml
<record id="cron_skill_sync" model="cron.task">
    <field name="name">Pi: synka skills</field>
    <field name="technical_name">skill_sync</field>
    <field name="model_name">ai.skill</field>
    <field name="method_name">_sync_from_filesystem</field>
    <field name="cadence">daily</field>
    <field name="module">ai_agent_core</field>
</record>
```

Motorn kör den via `cron_daily`. Ingen `nextcall`, ingen aritmetik.

## De fem kadenserna

| Kadens  | Tick-cron    | Spridning                          |
|---------|--------------|------------------------------------|
| `min`   | var 5:e min  | ingen — kör varje gång             |
| `hour`  | varje timme  | ingen — kör när > 1 tim sedan sist |
| `daily` | 1 gång/dygn  | över en timme (`hash % 60`)        |
| `week`  | 1 gång/vecka | över ett dygn (`hash % 1440`)      |
| `month` | 1 gång/månad | över en vecka (`hash % 10080`)     |

Spridningen är **deterministisk**: `sha256(technical_name) % fönster`. Samma
uppgift körs vid samma klockslag varje period — inte slumpmässigt — men olika
uppgifter sprids över fönstret så de inte krockar.

**Varför 5 minuter och inte 1:** `_heartbeat_all` m.fl. har redan en intern
5-minuterskontroll. När cron:en körde varje minut var 4 av 5 väckningar
garanterat slöseri.

## Tre utlösartyper — en körväg

```
Salt-deploy ──┐
Webhook ──────┤──► cron.task._run()
Manuell knapp ┤
Tick ─────────┘
```

### 1. Schemalagd

Tick-cron:en anropar `model._cron_tick('<kadens>')`. Den hämtar aktiva
uppgifter i kadensen, filtrerar på `_is_due()`, sorterar på `sequence, id`
och kör var och en.

### 2. Händelsedriven (webhook)

```bash
curl -X POST https://<host>/cron/trigger/skill_sync \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"call","params":{}}'
```

Svarar **alltid HTTP 200** — en avsändare som får 4xx/5xx retry:ar i
oändlighet, och triggningen är inte idempotent (uppgiften körs).

| Situation     | Svar                                          |
|---------------|-----------------------------------------------|
| avstängd      | `{"status": "disabled"}`                      |
| fel/saknad token | `{"status": "error", "error": "Unauthorized"}` |
| okänt namn    | `{"status": "not_found", ...}`                |
| körning ok    | `{"status": "ok", "duration_ms": 3}`          |
| körning fel   | `{"status": "error", "error": "..."}`         |

Token: `cron_tick.webhook_token`, med fallback till
`saltstack.alert.webhook_token` — Salt-minions behöver därmed inte en andra
nyckel. Stängs av med `cron_tick.webhook_enabled = False`.

### 3. Manuell

Knappen **Kör nu** i formuläret (`action_run_now`). Nekar om uppgiften körs.

## Körning — motorn äger historiken

`_run()` är **ren**: den slår upp modellen, anropar metoden, returnerar
resultatet. Den rör aldrig `last_run`, `failure_count` eller `last_error`.

Motorn (`_cron_tick`, `_execute`) bokför efter körning. **En skrivpunkt, inte
två.** Om `_run()` satte `last_run` och sedan kastade skulle savepointen rulla
tillbaka skrivningen och motorn tro att uppgiften aldrig körts.

## Felisolering

Varje uppgift körs i egen savepoint:

```python
try:
    with self.env.cr.savepoint():
        task._run()
except Exception as exc:
    self.env.invalidate_all()          # ORM-cachen är korrupt efter rollback
    self.browse(task_id)._record_failure(exc, duration_ms)
```

⚠ `invalidate_all()` + `browse()` är **obligatoriskt**. Efter en rollback
pekar ORM-cachen på data som inte finns i databasen — att skriva till den
posten ger `could not serialize access due to concurrent update`.

Efter `max_failures` konsekutiva fel inaktiveras uppgiften automatiskt.

## Lås

Per uppgift: **sessionsbundet PostgreSQL advisory-lock**.

```python
lock_id = sha256(f'cron_task:lock:{technical_name}') % 2**31
self.env.cr.execute('SELECT pg_try_advisory_lock(%s)', (lock_id,))
```

⚠ **En villkorlig UPDATE räcker inte.** Odoo kör under `repeatable read`. Två
transaktioner kan båda se `locked_by` som tomt i sin snapshot och båda få
`rowcount == 1`. Verifierat i drift — två samtidiga processer körde samma
uppgift. Advisory-locket är atomiskt oavsett isolationsnivå.

`locked_by`/`locked_at` finns kvar som **information** (vem kör, sedan när) —
inte som själva låset.

⚠ Advisory-lås är **re-entranta inom samma session**. Två `_acquire_lock` i
samma anslutning ger båda `True`. Det är dokumenterat beteende — men det
betyder att ett test i en enda `odoo shell`-session inte kan bevisa ömsesidig
uteslutning. Använd två riktiga anslutningar.

⚠ Låset släpps i `finally`. Utan det hålls det till anslutningen stänger
(kan vara timmar i en worker) och uppgiften kan aldrig köras igen.

Per kadens: ett globalt `pg_try_advisory_lock` i `_cron_tick`, så två workers
inte kör samma kadens samtidigt.

## Fält

| Fält               | Beskrivning                                          |
|--------------------|------------------------------------------------------|
| `name`             | Läsbart namn                                          |
| `technical_name`   | Stabil identifierare (unik) — används av webhook + spridning |
| `module`           | Modulen som äger uppgiften                            |
| `model_name`       | Tekniskt modellnamn (sträng, inte FK)                 |
| `method_name`      | Metodnamn — anropas utan argument                     |
| `cadence`          | `min`/`hour`/`daily`/`week`/`month`                   |
| `sequence`         | Körordning inom kadensen                              |
| `timeout_seconds`  | Mjuk tidsgräns (mätande, inte avbrytande)             |
| `max_failures`     | Fel i följd innan auto-inaktivering                   |
| `last_run`         | Senast körd (ägs av motorn)                           |
| `last_duration_ms` | Varaktighet (ägs av motorn)                           |
| `failure_count`    | Fel i följd (ägs av motorn)                           |
| `last_error`       | Senaste felmeddelande                                 |
| `locked_by`        | Vem som kör (information)                             |
| `locked_at`        | Sedan när (information)                               |

`model_name`/`method_name` är **strängar**, inte en `ir.model`-FK. Det gör
uppgiften robust vid `--update`: en modul som avinstalleras ger ett tydligt
felmeddelande i stället för en kraschande FK.

## Tidsgränsen är mjuk

Python-trådar kan inte avbrytas säkert. `timeout_seconds` **mäter** och
loggar en varning — den avbryter inte. En uppgift som konsekvent överskrider
gränsen bör flyttas till `queue_job`.

## Kadensen är ett fält, inte ett namnprefix

Ett namnprefix (`daily_...`) kan inte litas på — någon byter namn och
schemat ändras tyst. `cadence`-fältet är sanningen.

## Installation

```bash
checkmodule -d <db> -m cron_tick
```

Modulen beror **endast på `base`**. `odoo-project`, `odoo-saltstack`,
`odoo-bifrost` och `odoo-keykeep` kan använda den utan att bero på
AI-stacken — `odoo-project` kan installeras utan `odoo-ai`.

## Migrering av befintlig `ir.cron`

1. Lägg uppgiften som `cron.task` i modulens data-XML.
2. Sätt den gamla `ir.cron` till `active = False` och prefixa namnet med
   `[MIGRERAD → cron.task]`.
3. **Radera inte** — behåll en månad för jämförelse.
4. Verifiera i drift innan städning.

## Felsökning

| Symtom | Trolig orsak |
|--------|--------------|
| Uppgiften körs aldrig | `active=False` (auto-inaktiverad efter `max_failures`?) — se `last_error` |
| `Modellen "X" finns inte` | Modulen är avinstallerad, eller `model_name` är felstavat |
| `Metoden "X" finns inte` | Metodnamnet fel, eller modulen uppgraderad |
| Uppgiften verkar hänga | `locked_by` satt — en worker kör. Kolla `locked_at` |
| `could not serialize access` | Skrivning efter rollback utan `invalidate_all()` |
| `search` på `is_overdue` ger 0 | Prefix-domänen fel — se `_search_is_overdue` |
