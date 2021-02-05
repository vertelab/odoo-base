import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class ResInterpreterGenderPreference(models.Model):
    _name = "res.interpreter.gender_preference"
    code = fields.Char()
    name = fields.Char()
