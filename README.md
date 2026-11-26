<!-- [![Runbot Status](https://runbot.odoo-community.org/runbot/badge/flat/${REPO_ID}/${BRANCH_NAME}.svg)](https://runbot.odoo-community.org/runbot/repo/github-com-oca-${REPO_NAME}-${REPO_ID}) -->
[![Build Status](https://travis-ci.com/OCA/${REPO_NAME}.svg?branch=${BRANCH_NAME})](https://travis-ci.com/OCA/${REPO_NAME})
<!-- [![codecov](https://codecov.io/gh/OCA/${REPO_NAME}/branch/${BRANCH_NAME}/graph/badge.svg)](https://codecov.io/gh/OCA/${REPO_NAME}) -->

# ${REPO_NAME_VERBOSE}

${REPO_DESCRIPTION}

<!-- prettier-ignore-start -->
[//]: # (addons)
This part will be replaced when running the oca-gen-addons-table script from OCA/maintainer-tools.
[//]: # (end addons)
<!-- prettier-ignore-end -->

## Porteringsstatus — Odoo 19.0

Den här grenen är Odoo 19.0. Tabellen beskriver bara 19.0.

Genererad av `scripts/porting-status.py` — handredigera inte.

| Modul | Beskrivning | Porteringsstatus |
|---|---|---|
| `attachment_exif` | Extract and display EXIF metadata from image attachments. | ok |
| `attachment_notebook` | Adds a notebook for other modules to populate with more functionality. | ok |
| `auth_admin` | Unified password for admin. | ok |
| `auth_signup_nosignup` | Removes new user signup from the front page. | ok |
| `base_46elks_send_sms` | Sends SMS messages through the 46elks gateway. | ok |
| `base_ai` | OKF-indexering av res.partner, res.company och res.users | blocked by web_pwa_push (repo) |
| `base_allow_marketing` | Opt-in for marketing email. | ok |
| `base_booking` | A base module to allow booking integrations in any flow. | ok |
| `base_booking_mail` | Sends emails for bookings. | ok |
| `base_booking_payment` | Booking payment. | ok |
| `base_booking_website` | Adds booking types to the website. | ok |
| `base_dav` | Access Odoo data as calendar or address book | blocked by radicale (python) |
| `base_health_deep` | Registry-aware health endpoint for load balancers and monitoring | ok |
| `base_migration_helper` | Helpers for migrating data between Odoo instances. | ok |
| `base_partner_find_duplicate` | The module adds a new meny choice under Configuration in Contacts. This meny … | ok |
| `base_partner_se` | Localized Partner Records. | ok |
| `base_partner_template` | Marks contacts as templates for quick creation. | ok |
| `base_replace_user` | Replace User on Records. | ok |
| `base_security_classification` | Security Classification. | blocked by server_environment_data_encryption (OCA) |
| `base_serp` | Track Search Engine Results Page (SERP) positions for domains and keywords. | blocked by fake_useragent (python) |
| `base_user_role_default` | Extends the User Roles to add portal user to res.users.role. | blocked by base_user_role (core) |
| `base_user_role_mass_addition` | Extends the User Roles to enable assiging several users to a role, at the same … | blocked by base_user_role (core) |
| `boat_booking` | Booking of boats and other bookable resources. | ok |
| `cron_tick` | Declarative scheduling — one engine, five cadences | ok |
| `discuss_multi_thread` | Multi Thread in Odoo Discuss. | ok |
| `html_field_code_view` | Show Code View on HTML Field. | blocked by web_editor (core) |
| `ir_module_extra_repos` | Add an extra repos. | ok |
| `ir_module_xl2install` | Install modules from a excel document. | ok |
| `matomo_website_analytics` | Matomo integration for website analytics. | blocked by fake_useragent (python) |
| `model_import_directory` | Imports records from a directory of files. | blocked by edi_base (Vertel) |
| `partner_allabolag` | Enrich partner with data from Allabolag. | blocked by allabolag (python) |
| `partner_allabolag_bankruptcy` | Track Allabolag Partner Bankruptcy. | blocked by allabolag (python) |
| `partner_anonymization_rule` | Partner Anonymization Rule for GDPR compliance | blocked by privacy_partner_to_be_forgotten (Vertel) |
| `partner_builtwith` | Enrich partner with technical information. | blocked by builtwith (python) |
| `partner_company_registry` | Adds a Partner Registry field to the partner object. | ok |
| `partner_contract` | Short (1 phrase/line) summary of the module's purpose, used as subtitle on … | ok |
| `partner_counterpart` | Partner Counterpart. | ok |
| `partner_enrich_base` | Base module for partner data enrichment. | ok |
| `partner_flip_firstname` | Change position. Replace by the other. | blocked by partner_firstname (repo) |
| `partner_flip_zip_city` | Change order to Zip, State, City. | ok |
| `partner_foretagssok` | Enrich partner with data from FöretagsAPI.se | ok |
| `partner_gender` | Adds a "Personal information" tab on res_partners with a gender field. | ok |
| `partner_get_logos` | Get logos ========= Get logos. Features: - Extends Odoo: Builds on existing … | ok |
| `partner_legacy_id` | Stores legacy IDs on contacts. | ok |
| `partner_portal_user` | Adds a field on partners that shows if the partner is connected to a portal … | ok |
| `partner_sni` | SNI Swedish Standard Industrial Classification. | ok |
| `partner_ssn` | Adds social security number to partners. | ok |
| `partner_uuid` | Adds a partner_uuid field to partners. | ok |
| `pos_restaurant_booking` | This module lets you manage online reservations for restaurant tables. | ok |
| `record_export_to_xml` | Export Records to XML. | ok |
| `res_config_quests` | Add quests field to res.config.settings. | ok |
| `serp_serpapi` | SerpAPI provider for reliable SERP tracking. | blocked by fake_useragent (python) |
| `users_rights_listed` | Adds a UserGroup field to the res_users tree-view in debug-mode. | ok |
| `web_menu_no_cache` | Send no-cache for /web/webclient/load_menus so menu updates always reach … | ok |
| `workspace_onboarding` | Sammanhållande onboardingskurs: navigering, mobil och PWA | ok |
