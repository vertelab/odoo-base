from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_portaluser = fields.Boolean(compute="set_portalbool", readonly=True)

    def set_portalbool(self):
        self.is_portaluser = False
        for rec in self:
            for user in rec.user_ids:
                if user.has_group('base.group_portal'):
                    rec.is_portaluser = True
                else:
                    rec.is_portaluser = False
