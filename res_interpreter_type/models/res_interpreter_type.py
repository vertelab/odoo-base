import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class ResInterpreterType(models.Model):
    _name = "res.interpreter.type"
    _description = "RES Intepreter Type"

    code = fields.Char()
    name = fields.Char()
