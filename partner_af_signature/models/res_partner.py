import logging
import re
from datetime import date
from odoo.exceptions import ValidationError

from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    af_signature = fields.Char(string="AF Signature")
