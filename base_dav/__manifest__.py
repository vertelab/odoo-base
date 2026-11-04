# Copyright 2018 Therp BV <https://therp.nl>
# Copyright 2019-2020 initOS GmbH <https://initos.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Base: CalDAV and CardDAV",
    "version": "18.0.1.0.4",
    "author": "Vertel Sverige AB, initOS GmbH,Therp BV,Odoo Community Association (OCA)",
    "website": "https://vertel.se/apps/odoo-base/base_dav",
    "license": "AGPL-3",
    "category": "Extra Tools",
    "summary": "Access Odoo data as calendar or address book",
    "depends": [
        'base',
    ],
    "demo": [
        "demo/dav_collection.xml",
    ],
    "data": [
        "views/dav_collection.xml",
        'security/ir.model.access.csv',
    ],
    "external_dependencies": {
        'python': ['radicale'],
    },
    # ------------------------------------------------------------------
    # INSTALLABLE: False — 2026-09-22
    #
    # Detta är OCA/Radicale-sparet för DAV. Vertel har ett EGET, fristaende
    # CalDAV-spar: calendar_caldav (endpoint /caldav/). Bada registrerar
    # /.well-known/caldav och kolliderar — bara ett far vara installerat.
    #
    # Beslut 2026-09-22: calendar_caldav ar standard (se README
    # "CalDAV: val av spar"). base_dav-sparet ar trasigt pa njannja:
    #   - PROPFIND /.dav/ -> 500
    #     (radicale/collection.py:113, odoo_collection=None for roten)
    #   - /.dav/__system__/1 -> 403 / 500
    # calendar_caldav ger DAV: 1, 2, calendar-access + RFC 6764 och
    # fungerar skarpt (GET/PUT/PROPFIND/OPTIONS).
    #
    # Konsekvens: aven calendar_dav, user_settings_dav, contact_carddav och
    # personal_contact_carddav (som beror pa base_dav) spärras — de tillhor
    # samma spar. Adressboks-funktionaliteten (CardDAV) saknar da
    # motsvarighet i calendar_caldav och far byggas separat om behov uppstar.
    #
        # Retired 2026-10-25: the Radicale-based DAV track is superseded by
    # calendar_caldav, which is the single CalDAV+CardDAV server for
    # ledningssystem. Both tracks registered /.well-known/caldav, and
    # whichever answered first won — the Radicale track answered and
    # returned an empty 207 for every client (DAVx5, Thunderbird,
    # Evolution). The routes are unregistered in the code, not here:
    # installable=False also stops Odoo from loading the module's
    # models, which broke res.ppartner and caldav.collection.
    "installable": True,
    "auto_install": False,
}
