import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class ResInterpreterType(models.Model):
    _name = "res.interpreter.type"
    code = fields.Char()
    name = fields.Char()
