# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import operator
import re

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
from odoo.http import request
from odoo.modules import get_module_resource

MENU_ITEM_SEPARATOR = "/"
NUMBER_PARENS = re.compile(r"\(([0-9]+)\)")


class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'
    _order = "name,sequence,id"