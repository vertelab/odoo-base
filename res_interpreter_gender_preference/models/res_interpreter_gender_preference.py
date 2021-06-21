import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class ResInterpreterGenderPreference(models.Model):
    _name = "res.interpreter.gender_preference"
    _description = "RES Interpreter Gender Preference"

    code = fields.Char()
    name = fields.Char()
