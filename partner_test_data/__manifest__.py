# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Fenix Contacts Test Data",
    "version": "12.0.1.0.2",
    "author": "Vertel AB",
    "license": "AGPL-3",
    "website": "https://vertel.se/",
    "description": """
        This module adds testdata to be used in the KVL and STOM-projects. 
        The source of the data is here: https://confluence.ams.se/pages/viewpage.action?pageId=76597519
    """,
    "category": "Tools",
    "depends": [
        "base",
        "contacts",
    ],
    "external_dependencies": [],
    "data": [
        'data/res_company.xml',
        'data/res_partner.xml',
        'data/res_user.xml',
    ],
    "application": True,
    "installable": True,
}
