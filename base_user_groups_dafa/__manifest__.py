# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "DAFA User Groups",
    "version": "12.0.1.0.5",
    "author": "Arbetsformedlingen",
    "license": "AGPL-3",
    "description": """User groups for the DAFA server. Access rules are added in each module.\n
    AFC-1590 Added Supportgroups for 1st and 2nd line. Fixed version numbers\n
    AFC-1747 Update in translation.\n
    AFC-2117 Added New group for translation accountants.\n
    AFC-2090 Added SalesRole to AccountingRead-group \n
    """,
    "website": "https://arbetsformedlingen.se/",
    "category": "Security",
    "depends": [
        "outplacement",
        "web_dashboard_dafa",
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
