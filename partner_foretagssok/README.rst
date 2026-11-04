FöretagsAPI Partner Enrichment
==============================

Enrich ``res.partner`` records with official Swedish company data from
`FöretagsAPI.se <https://foretagsapi.se>`_.

The module replaces the scraping-based ``partner_allabolag`` approach with a
clean REST integration against ``https://data.foretagsapi.se``.

Features
--------

* Enrich individual or selected partners from the contact form or via a server
  action.
* Fetches: name, organisation number, VAT, address, SNI codes, business
  description, registration status, revenue/employee estimates and financial
  key figures.
* Integrates with ``partner_sni``: SNI codes are looked up or created and
  linked to the partner.
* Find other companies with the same SNI code and create them as contacts.
* Configurable API key and base URL in Settings -> Contacts.

Configuration
-------------

1. Place your API key in ``partner_foretagssok/.env`` as
   ``FORETAGSSOK_API_KEY=<key>``. It is loaded automatically when the module
   is installed.
2. Alternatively, enter the key in Settings -> Contacts -> FöretagsAPI.

Usage
-----

* Open a company contact and click **Enrich from FöretagsAPI**.
* If the partner has no organisation number, the module searches by name and
  uses the only match. When several matches exist, a notification is posted
  and the user must add an organisation number.
* When the partner has an SNI code, click **Find Similar Companies** to search
  for other companies in the same branch.

Dependencies
------------

* ``partner_enrich_base``
* ``partner_company_registry``
* ``partner_sni``
* ``mail``

License
-------

AGPL-3
