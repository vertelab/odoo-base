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

## Porteringsstatus

18.0 är baseline. 19.0/20.0 visar om p-filen har ett villkor för utgåvan
— inte om grenen finns. Blockerare är `depends` som saknas i 20.0
(kärna + alla 20.0-grenar).

| Modul | Beskrivning | Manifest | p-fil | 19.0 | 20.0 | Blockerare |
|---|---|---|---|---|---|---|
| attachment_exif | Extract and display EXIF metadata from image attachments. | 1.0.0 | 1 | — | — | — |
| attachment_notebook | Adds a notebook for other modules to populate with more f... | 0.1.0 | 0 | — | — | — |
| auth_admin | Unified password for admin. | 1.0.0 | 3 | — | — | — |
| auth_signup_nosignup | Removes new user signup from the front page. | 1.0.0 | 0 | — | — | — |
| base_46elks_send_sms | Sends SMS messages through the 46elks gateway. | 0.0.0 | 0 | — | — | — |
| base_ai | OKF-indexering av res.partner, res.company och res.users | 1.0.0 | 1 | — | — | — |
| base_allow_marketing | Opt-in for marketing email. | 1.0.0 | 1 | — | — | — |
| base_booking | A base module to allow booking integrations in any flow. | 1.3.0 | 6 | — | ✓ | — |
| base_booking_mail | Sends emails for bookings. | 1.0.0 | 1 | — | — | — |
| base_booking_payment | Booking payment. | 1.0.0 | 1 | — | — | — |
| base_booking_website | Adds booking types to the website. | 1.0.0 | 3 | — | ✓ | — |
| base_dav | Access Odoo data as calendar or address book | 1.0.0 | 1 | — | — | — |
| base_migration_helper | Helpers for migrating data between Odoo instances. | 1.0.0 | 1 | — | — | — |
| base_partner_find_duplicate | The module adds a new meny choice under Configuration in ... | 0.0.0 | 1 | — | — | — |
| base_partner_se | Localized Partner Records. | 1.0.0 | 0 | — | — | — |
| base_partner_template | Marks contacts as templates for quick creation. | 1.0.0 | 1 | — | — | — |
| base_replace_user | Replace User on Records. | 1.0.0 | 2 | — | — | — |
| base_security_classification | Security Classification. | 1.0.0 | 0 | — | — | `server_environment_data_encryption` |
| base_serp | Track Search Engine Results Page (SERP) positions for dom... | 1.3.0 | 1 | — | — | — |
| base_user_role_default | Extends the User Roles to add portal user to res.users.role. | 0.1.0 | 1 | ✓ | — | `base_user_role` |
| base_user_role_mass_addition | Extends the User Roles to enable assiging several users t... | 1.0 | 7 | — | ✓ | `base_user_role` |
| boat_booking | Booking of boats and other bookable resources. | 1.0.0 | 0 | — | — | — |
| discuss_multi_thread | Multi Thread in Odoo Discuss. | 1.0.0 | 0 | — | — | — |
| html_field_code_view | Show Code View on HTML Field. | 0.1.0 | 0 | — | — | `web_editor` |
| ir_module_extra_repos | Add an extra repos. | 1.0.0 | 0 | — | — | — |
| ir_module_xl2install | Install modules from a excel document. | 1.0.0 | 1 | — | — | — |
| matomo_website_analytics | Matomo integration for website analytics. | 1.0.0 | 0 | — | — | — |
| model_import_directory | Imports records from a directory of files. | 1.0.0 | 1 | — | — | `edi_base` |
| partner_allabolag | Enrich partner with data from Allabolag. | 1.1.0 | 0 | — | — | — |
| partner_allabolag_bankruptcy | Track Allabolag Partner Bankruptcy. | 1.1.0 | 0 | — | — | — |
| partner_anonymization_rule | Partner Anonymization Rule for GDPR compliance | 1.0.0 | 1 | — | — | `privacy_partner_to_be_forgotten` |
| partner_builtwith | Enrich partner with technical information. | 1.1.0 | 0 | — | — | — |
| partner_company_registry | Adds a Partner Registry field to the partner object. | 1.0.0 | 0 | — | — | — |
| partner_contract | Short (1 phrase/line) summary of the module's purpose, us... | 1.0 | 7 | ✓ | — | — |
| partner_counterpart | Partner Counterpart. | 1.0.0 | 1 | — | — | — |
| partner_enrich_base | Base module for partner data enrichment. | 1.1.0 | 0 | — | — | — |
| partner_flip_firstname | Change position. Replace by the other. | 0.2.0 | 0 | — | — | `partner_firstname` |
| partner_flip_zip_city | Change order to Zip, State, City. | 1.1.0 | 0 | — | — | — |
| partner_foretagssok | Enrich partner with data from FöretagsAPI.se | 1.0.0 | 1 | — | — | — |
| partner_gender | Adds a "Personal information" tab on res_partners with a ... | 0.1.0 | 0 | — | — | — |
| partner_get_logos | Get logos. | 0.1.0 | 0 | — | — | — |
| partner_legacy_id | Stores legacy IDs on contacts. | 1.0.0 | 0 | — | — | — |
| partner_portal_user | Adds a field on partners that shows if the partner is con... | 0.1.0 | 0 | — | — | — |
| partner_sni | SNI Swedish Standard Industrial Classification. | 1.0.0 | 1 | — | — | — |
| partner_ssn | Adds social security number to partners. | 0.1.0 | 0 | — | — | — |
| partner_uuid | Adds a partner_uuid field to partners. | 0.1.0 | 0 | — | — | — |
| pos_restaurant_booking | This module lets you manage online reservations for resta... | 1.0.0 | 0 | — | — | — |
| record_export_to_xml | Export Records to XML. | 0.1.1 | 1 | — | — | — |
| res_config_quests | Add quests field to res.config.settings. | 1.0.0 | 0 | — | — | — |
| serp_serpapi | SerpAPI provider for reliable SERP tracking. | 1.0.0 | 0 | — | — | — |
| users_rights_listed | Adds a UserGroup field to the res_users tree-view in debu... | 0.0.1 | 1 | — | — | — |
| web_menu_no_cache | Send no-cache for /web/webclient/load_menus so menu updat... | 1.0.0 | 0 | — | — | — |
| workspace_onboarding | Sammanhållande onboardingskurs: navigering, mobil och PWA | 1.0.0 | 0 | — | — | — |
