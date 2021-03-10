# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution, third party addon
#    Copyright (C) 2004-2020 Vertel AB (<http://vertel.se>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api, _
import logging

from odoo.exceptions import Warning, ValidationError

_logger = logging.getLogger(__name__)


class ResCountryState(models.Model):
    _inherit = "res.country.state"
    
    @api.multi
    def name_get(self):
        """ name_get() -> [(id, name), ...]

        Returns a textual representation for the records in ``self``.
        Name is partner_name if set, else name.

        :return: list of pairs ``(id, text_repr)`` for each records
        :rtype: list(tuple)
        """
        # super(ResCountryState, self).name_get()
        result = []
        for state in self:
                result.append((state.id, "%s %s" % (state.code, state.name)))
        return result
