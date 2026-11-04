# partner_foretagssok

## Purpose
Enrich `res.partner` records with official Swedish company data from
[FöretagsAPI.se](https://foretagsapi.se) via the REST API at
`https://data.foretagsapi.se`.

The module was created as a clean replacement for `partner_allabolag`, which
relied on web scraping through Tor.

## Data flow
1. User triggers enrichment from the partner form or a server action.
2. If `company_registry` is set, the module calls `POST /v1/bulk`.
3. Otherwise it calls `POST /v1/search` by name.
4. The response is mapped to Odoo fields: name, address, VAT, SNI codes,
   business description, status, estimates and financials.
5. A chatter message summarises the enrichment.

## SNI integration
The module depends on `partner_sni`. SNI codes returned by the API are looked
up or created in `res.sni` and linked through `sni_id` and `sni_ids`.

The **Find Similar Companies** action uses `POST /v1/sni/search` to find other
companies with the same SNI code. Results are shown in a transient wizard and
can be created as new partners.

## Configuration
API key and base URL are stored in `ir.config_parameter`:
* `partner_foretagssok.api_key`
* `partner_foretagssok.base_url` (default `https://data.foretagsapi.se`)

On installation the module attempts to load `FORETAGSSOK_API_KEY` from
`partner_foretagssok/.env`.

## Models
* `res.partner` - extended with FöretagsAPI-specific fields and enrichment
  methods.
* `res.partner.financials` - one row per fiscal year with key figures from
  digital annual reports.
* `foretagssok.similar.wizard` / `foretagssok.similar.wizard.line` - transient
  models for the SNI similarity search.

## Security
Access rights are defined in `security/ir.model.access.csv`.

## External dependencies
Only Odoo-bundled libraries. HTTP calls use `requests` (shipped with Odoo).
