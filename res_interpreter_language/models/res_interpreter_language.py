import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class ResInterpreterLanguage(models.Model):
    _name = "res.interpreter.language"
    code = fields.Char()
    name = fields.Char()
