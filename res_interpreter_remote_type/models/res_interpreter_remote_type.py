import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class ResInterpreterRemoteType(models.Model):
    _name = "res.interpreter.remote_type"
    code = fields.Char()
    name = fields.Char()
