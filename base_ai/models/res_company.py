# -*- coding: utf-8 -*-
"""res.company — OKF-indexerbar (base_ai).

Modellen äger sina KÄLLOR; `ai.okf.mixin` äger fälten och flaggan.

VARFÖR res.company BÄR MIXINEN: den är en av de mest länkade modellerna i
systemet. När den bär mixinen blir relationsfält på ANDRA modeller
automatiskt länkar — `_okf_links_source()` i mixinen länkar bara dit
målet har mixinen. Regeln är självregistrerande.
"""

from odoo import models


class ResCompany(models.Model):
    _name = 'res.company'
    _inherit = ['res.company', 'ai.okf.mixin']

    # ── Källor ─────────────────────────────────────────────────────────
    #
    # `okf_body`, `okf_tags` och `okf_links` är GENERISKA i mixinen:
    #   okf_body  = alla HTML/Text-fält + name
    #   okf_tags  = fält med 'tag' i namn eller målmodell
    #   okf_links = relationsfält där målet bär mixinen
    #
    # Bryggan skriver därför bara det som är specifikt för modellen.

    def _okf_artifact_type(self):
        """Bryggans egen typ (okf-mixin D12)."""
        return 'company'

    def _okf_dirty_fields(self):
        """Fält vars ändring gör OKF-fälten inaktuella.

        Bara innehållsfält. Tekniska fält (login_date, last_login) och
        räknare ändras ofta och säger inget om texten.
        """
        return {'name', 'email', 'phone', 'website', 'vat', 'street', 'city', 'zip', 'active'}

    def _okf_skip_reason(self):
        """Arkiverad post = "tomt just nu", inte "tomt för alltid"."""
        return None

    # ── Registrering (okf-mixin D11) ───────────────────────────────────

    def _register_hook(self):
        """Registrera modellen för dirty-indexering.

        Registrering, inte överridning: `_okf_indexable_models()` är
        `@api.model` på en abstrakt modell (mätt på luke18 2026-09-22).
        """
        res = super()._register_hook()
        self.env['ai.okf.mixin']._okf_register_indexable('res.company')
        return res
