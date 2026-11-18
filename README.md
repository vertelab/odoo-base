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

## Porteringsstatus — Odoo 18.0

Den här grenen är Odoo 18.0. Tabellen beskriver bara 18.0.

Genererad av `scripts/porting-status.py` — handredigera inte.

| Modul | Funktionsbeskrivning | Porteringsstatus |
|---|---|---|
| `attachment_exif` | Extract and display EXIF metadata from image attachments. | ✓ `18.0.1.0.0` ✗ · 2 p-filer<br>⚠ `base` (finns inte i något addons-repo) |
| `attachment_notebook` | Adds a notebook for other modules to populate with more functionality. | ✓ `18.0.0.1.0` ✗ · 0 p-filer<br>⚠ `base` (finns inte i något addons-repo) |
| `auth_admin` | Unified password for admin. | ✓ `1.0.0` ✗ · 3 p-filer<br>⚠ `base` (finns inte i något addons-repo) |
| `auth_signup_nosignup` | Removes new user signup from the front page. | ✓ `18.0.1.0.0` ✗ · 0 p-filer<br>⚠ `base` (finns inte i något addons-repo)<br>`auth_signup` (finns inte i något addons-repo) |
| `base_46elks_send_sms` | Sends SMS messages through the 46elks gateway. | ✓ `18.0.0.0.0` ✗ · 0 p-filer<br>⚠ `sms` (finns inte i något addons-repo) |
| `base_ai` | OKF-indexering av res.partner, res.company och res.users | ✓ `18.0.1.0.0` ✗ · 1 p-fil<br>⚠ `base` (finns inte i något addons-repo) |
| `base_allow_marketing` | Opt-in for marketing email. | ✓ `18.0.1.0.0` ✗ · 1 p-fil<br>⚠ `auth_signup` (finns inte i något addons-repo)<br>`portal` (finns inte i något addons-repo) |
| `base_booking` | A base module to allow booking integrations in any flow. | ✓ `18.0.1.3.0` ✗ · 6 p-filer<br>⚠ `calendar` (finns inte i något addons-repo)<br>`phone_validation` (finns inte i något addons-repo)<br>`portal` (finns inte i något addons-repo)<br>`resource` (finns inte i något addons-repo)<br>`mail` (finns inte i något addons-repo) |
| `base_booking_mail` | Sends emails for bookings. | ✓ `18.0.1.0.0` install · 1 p-fil |
| `base_booking_payment` | Booking payment. | ✓ `18.0.1.0.0` ✗ · 1 p-fil<br>⚠ `account_payment` (finns inte i något addons-repo) |
| `base_booking_website` | Adds booking types to the website. | ✓ `18.0.1.0.0` ✗ · 3 p-filer<br>⚠ `website_partner` (finns inte i något addons-repo) |
| `base_dav` | Access Odoo data as calendar or address book | ✓ `18.0.1.0.4` ✗ · 2 p-filer<br>⚠ `base` (finns inte i något addons-repo) |
| `base_health_deep` | Registry-aware health endpoint for load balancers and monitoring | ✓ `18.0.1.0.0` ✗ · 0 p-filer<br>⚠ `base` (finns inte i något addons-repo) |
| `base_migration_helper` | Helpers for migrating data between Odoo instances. | ✓ `18.0.1.0.0` ✗ · 1 p-fil<br>⚠ `mail` (finns inte i något addons-repo) |
| `base_partner_find_duplicate` | The module adds a new meny choice under Configuration in Contacts. This meny choice will present the existing contact, sorted by matching names, email, or phone number. | ✓ `18.0.0.0.0` ✗ · 1 p-fil<br>⚠ `contacts` (finns inte i något addons-repo) |
| `base_partner_se` | Localized Partner Records. | ✓ `18.0.1.0.0` ✗ · 0 p-filer<br>⚠ `mail` (finns inte i något addons-repo) |
| `base_partner_template` | Marks contacts as templates for quick creation. | ✓ `18.0.1.0.0` ✗ · 1 p-fil<br>⚠ `contacts` (finns inte i något addons-repo) |
| `base_replace_user` | Replace User on Records. | ✓ `18.0.1.0.0` ✗ · 3 p-filer<br>⚠ `sale` (finns inte i något addons-repo)<br>`sale_management` (finns inte i något addons-repo)<br>`sales_team` (finns inte i något addons-repo)<br>`base` (finns inte i något addons-repo) |
| `base_security_classification` | Security Classification. | ✓ `18.0.1.0.0` ✗ · 0 p-filer<br>⚠ `base` (finns inte i något addons-repo)<br>`mail` (finns inte i något addons-repo) |
| `base_serp` | Track Search Engine Results Page (SERP) positions for domains and keywords. | ✓ `18.0.1.3.0` ✗ · 1 p-fil<br>⚠ `base_setup` (finns inte i något addons-repo)<br>`web` (finns inte i något addons-repo)<br>`website` (finns inte i något addons-repo) |
| `base_user_role_default` | Extends the User Roles to add portal user to res.users.role. | ✓ `18.0.0.1.0` ✗ · 1 p-fil<br>⚠ `base` (finns inte i något addons-repo)<br>`base_user_role` (finns inte i något addons-repo)<br>`portal` (finns inte i något addons-repo) |
| `base_user_role_mass_addition` | Extends the User Roles to enable assiging several users to a role, at the same time. | ✓ `1.0` ✗ · 7 p-filer<br>⚠ `base_user_role` (finns inte i något addons-repo)<br>`base` (finns inte i något addons-repo) |
| `boat_booking` | Booking of boats and other bookable resources. | ✓ `18.0.1.0.0` ✗ · 0 p-filer<br>⚠ `website` (finns inte i något addons-repo) |
| `cron_tick` | Declarative scheduling — one engine, five cadences | ✓ `2.5.0` ✗ · 6 p-filer<br>⚠ `base` (finns inte i något addons-repo)<br>`mail` (finns inte i något addons-repo) |
| `discuss_multi_thread` | Multi Thread in Odoo Discuss. | ✓ `18.0.1.0.0` ✗ · 0 p-filer<br>⚠ `base` (finns inte i något addons-repo) |
| `html_field_code_view` | Show Code View on HTML Field. | ✓ `18.0.0.1.0` ✗ · 0 p-filer<br>⚠ `web_editor` (finns inte i något addons-repo) |
| `ir_module_extra_repos` | Add an extra repos. | ✓ `18.0.1.0.0` ✗ · 0 p-filer<br>⚠ `base` (finns inte i något addons-repo) |
| `ir_module_xl2install` | Install modules from a excel document. | ✓ `18.0.1.0.0` ✗ · 1 p-fil<br>⚠ `base` (finns inte i något addons-repo) |
| `matomo_website_analytics` | Matomo integration for website analytics. | ✓ `18.0.1.0.0` install · 0 p-filer |
| `model_import_directory` | Imports records from a directory of files. | ✓ `18.0.1.0.0` ✗ · 1 p-fil<br>⚠ `base_setup` (finns inte i något addons-repo) |
| `partner_allabolag` | Enrich partner with data from Allabolag. | ✓ `18.0.2.0.0` ✗ · 0 p-filer<br>⚠ `contacts` (finns inte i något addons-repo) |
| `partner_allabolag_bankruptcy` | Track Allabolag Partner Bankruptcy. | ✓ `18.0.1.1.0` ✗ · 0 p-filer<br>⚠ `base` (finns inte i något addons-repo) |
| `partner_anonymization_rule` | Partner Anonymization Rule for GDPR compliance | ✓ `18.0.1.0.0` install · 1 p-fil |
| `partner_builtwith` | Enrich partner with technical information. | ✓ `18.0.1.1.0` install · 0 p-filer |
| `partner_company_registry` | Adds a Partner Registry field to the partner object. | ✓ `18.0.1.0.0` ✗ · 0 p-filer<br>⚠ `base` (finns inte i något addons-repo) |
| `partner_contract` | Short (1 phrase/line) summary of the module's purpose, used as subtitle on modules listing or apps.odoo.com | ✓ `1.0` ✗ · 7 p-filer<br>⚠ `base_setup` (finns inte i något addons-repo) |
| `partner_counterpart` | Partner Counterpart. | ✓ `18.0.1.0.0` ✗ · 1 p-fil<br>⚠ `base` (finns inte i något addons-repo)<br>`contacts` (finns inte i något addons-repo)<br>`sales_team` (finns inte i något addons-repo)<br>`account` (finns inte i något addons-repo) |
| `partner_enrich_base` | Base module for partner data enrichment. | ✓ `18.0.2.0.0` ✗ · 0 p-filer<br>⚠ `partner_autocomplete` (finns inte i något addons-repo)<br>`contacts` (finns inte i något addons-repo) |
| `partner_flip_firstname` | Change position. Replace by the other. | ✓ `18.0.0.2.0` install · 0 p-filer |
| `partner_flip_zip_city` | Change order to Zip, State, City. | ✓ `18.0.1.1.0` ✗ · 0 p-filer<br>⚠ `base` (finns inte i något addons-repo) |
| `partner_foretagssok` | Enrich partner with data from FöretagsAPI.se | ✓ `18.0.2.0.0` ✗ · 1 p-fil<br>⚠ `mail` (finns inte i något addons-repo) |
| `partner_gender` | Adds a "Personal information" tab on res_partners with a gender field. | ✓ `18.0.0.1.0` install · 0 p-filer |
| `partner_get_logos` | Get logos ========= Get logos. Features: - Extends Odoo: Builds on existing Odoo models. | ✓ `18.0.2.0.0` install · 0 p-filer |
| `partner_legacy_id` | Stores legacy IDs on contacts. | ✓ `18.0.1.0.0` ✗ · 0 p-filer<br>⚠ `contacts` (finns inte i något addons-repo) |
| `partner_portal_user` | Adds a field on partners that shows if the partner is connected to a portal user. | ✓ `18.0.0.1.0` ✗ · 0 p-filer<br>⚠ `contacts` (finns inte i något addons-repo) |
| `partner_sni` | SNI Swedish Standard Industrial Classification. | ✓ `18.0.1.0.0` ✗ · 1 p-fil<br>⚠ `contacts` (finns inte i något addons-repo) |
| `partner_ssn` | Adds social security number to partners. | ✓ `18.0.0.1.0` ✗ · 0 p-filer<br>⚠ `contacts` (finns inte i något addons-repo) |
| `partner_uuid` | Adds a partner_uuid field to partners. | ✓ `18.0.0.1.0` ✗ · 0 p-filer<br>⚠ `contacts` (finns inte i något addons-repo) |
| `pos_restaurant_booking` | This module lets you manage online reservations for restaurant tables. | ✓ `18.0.1.0.0` ✗ · 3 p-filer<br>⚠ `pos_restaurant` (finns inte i något addons-repo) |
| `record_export_to_xml` | Export Records to XML. | ✓ `18.0.0.1.1` ✗ · 1 p-fil<br>⚠ `base` (finns inte i något addons-repo)<br>`event` (finns inte i något addons-repo)<br>`hr` (finns inte i något addons-repo)<br>`sale` (finns inte i något addons-repo)<br>`project` (finns inte i något addons-repo) |
| `res_config_quests` | Add quests field to res.config.settings. | ✓ `18.0.1.0.0` ✗ · 0 p-filer<br>⚠ `base_setup` (finns inte i något addons-repo) |
| `serp_serpapi` | SerpAPI provider for reliable SERP tracking. | ✓ `18.0.1.0.0` install · 0 p-filer |
| `users_rights_listed` | Adds a UserGroup field to the res_users tree-view in debug-mode. | ✓ `18.0.0.0.1` ✗ · 1 p-fil<br>⚠ `base` (finns inte i något addons-repo) |
| `web_menu_no_cache` | Send no-cache for /web/webclient/load_menus so menu updates always reach clients. | ✓ `18.0.1.0.0` ✗ · 0 p-filer<br>⚠ `web` (finns inte i något addons-repo) |
| `workspace_onboarding` | Sammanhållande onboardingskurs: navigering, mobil och PWA | ✓ `18.0.2.0.0` ✗ · 0 p-filer<br>⚠ `website_slides` (finns inte i något addons-repo) |
