# -*- coding: utf-8 -*-
{
    'name': 'Base: AI',
    'version': '18.0.1.0.0',
    'summary': 'OKF-indexering av res.partner, res.company och res.users',
    'category': 'Hidden',
    'author': 'Vertel AB',
    'website': 'https://vertel.se',
    'license': 'AGPL-3',
    'description': """
        Bryggmodul för OKF-indexering av Odoo:s basmodeller.

        Lägger `ai.okf.mixin` på res.partner, res.company och res.users så
        att de blir OKF-koncept.

        VARFÖR DESSA TRE: de är de mest länkade modellerna i systemet.
        När de bär mixinen blir relationsfält på ANDRA modeller automatiskt
        länkar — `crm.lead.partner_id` blir en länk utan att crm_ai ändras.
        Regeln är självregistrerande (okf-mixin, `_okf_links_source`).

        Modellerna äger sina KÄLLOR; mixinen i ai_agent_core äger fälten
        och flaggan. Ingen domän nämns i kärnan.
    """,
    'depends': [
        'ai_agent_core',
        'base',
    ],
    'data': [
        'data/okf_artifact_types_base.xml',
    ],
    'demo': [],
    'application': False,
    'installable': True,
    'auto_install': False,
}
