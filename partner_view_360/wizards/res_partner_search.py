# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution, third party addon
#    Copyright (C) 2004-2019 Vertel AB (<http://vertel.se>).
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
from datetime import date
_logger = logging.getLogger(__name__)
from odoo.exceptions import Warning


class ResPartnerSearchWizard(models.TransientModel):
    _name ="res.partner.employer.search.wizard"

    #gdpr_id = fields.Many2one('gdpr') #some gdpr object
    search_reason = fields.Selection(string="Search reason" ,selection=[('reason','Reason')])#
    search_string = fields.Char(string="Search")
    domain_selection = fields.Selection(string="domain", selection=[('is_employer','Employer')])
    company_registry = fields.Char(string="Company registry")

    @api.multi
    def search_employer(self):
        something = True #byt ut mot en check efter om det är ett eller många resultat
        view_type = "tree"
        view_id = "view_partner_employer_kanban"
        partner_id = self.env['res.partner'].search([('company_registry', '=', self.company_registry)]).mapped('id')
        if len(partner_id) > 0:
            partner_id = partner_id[0]
        else:
            raise Warning(_("No id found"))
        if something:
            view_type = "form"
            view_id = "view_partner_employer_form"
        return{
            'name': _('Employers'), #vad gör den?
            'domain':[('id', '=', partner_id)],
            'view_type': view_type,
            'res_model': 'res.partner',
            'view_id':  view_id,
            'view_mode': 'kanban,tree,form',
            'type': 'ir.actions.act_window',
        }
    

