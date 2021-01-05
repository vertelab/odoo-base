# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "DAFA User Groups",
    "version": "12.0.1.0.2",
    "author": "Arbetsformedlingen",
    "license": "AGPL-3",
    "description": "User groups for the DAFA server. Access rules are added in each module.\n
    AFC-1590 Added Supportgroups for 1st and 2nd line. Fixed version numbers",
    "website": "https://arbetsformedlingen.se/",
    "category": "Security",
    "depends": [
        "hr",
        "sale",
        "project",
    ],
    "data": [
        'security/security.xml',
    ],
    "application": False,
    "installable": True,
}
