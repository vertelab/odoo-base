from odoo import models, fields, api, _
from datetime import date
import logging
from odoo.exceptions import ValidationError
import re


_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    af_signature = fields.Char(string="Signature")
