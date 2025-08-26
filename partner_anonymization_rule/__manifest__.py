# Copyright (C) 2025 Cetmix OÜ
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

{
    "name": "Partner Anonymization Rule",
    "version": "18.0.1.0.0",
    "category": "Data Protection",
    "summary": "Partner Anonymization Rule for GDPR compliance",
    "author": "Vertel AB",
    "license": "LGPL-3",
    "website": "https://vertel.se",
    'repository': 'https://github.com/vertelab/odoo-base',
    "depends": ["privacy_partner_to_be_forgotten"],
    "data": [
        "security/ir.model.access.csv",
        "views/anonymization_rule_view.xml",
        "data/ir_cron.xml",
    ],
}
