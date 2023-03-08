from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_portaluser = fields.Boolean(compute="_set_portalbool", readonly=True)

    def _set_portalbool(self):
        self.is_portaluser = False
        for rec in self:
            for user in rec.user_ids:
                if user.has_group('base.group_portal'):
                    self.is_portaluser = True
