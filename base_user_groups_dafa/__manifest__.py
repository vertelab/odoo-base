# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "DAFA User Groups",
    "version": "12.0.0.1",
    "author": "Arbetsformedlingen",
    "license": "AGPL-3",
    "description": "User groups for the DAFA server. Access rules are added in each module.",
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
