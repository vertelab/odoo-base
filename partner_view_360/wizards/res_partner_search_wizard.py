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
from odoo.tools.safe_eval import safe_eval


# class ResPartnerEmployerSearchWizard(models.TransientModel):
#     _name = "res.partner.employer.search.wizard"

    #gdpr_id = fields.Many2one('gdpr') #some gdpr object
    # search_reason = fields.Selection(string="Search reason" ,selection=[('reason','Reason')])#
    # search_domain = fields.Char(string="Search Filter", default=[('company_registry', '=', '')])

    # @api.multi
    # def search_employer(self):
    #     raise Warning("Inte implementerat än")
    #     something = True #byt ut mot en check efter om det är ett eller många resultat
    #     view_type = "tree"
    #     view_id = "view_partner_employer_kanban"
    #     partner_id = self.env['res.partner'].search([('company_registry', '=', self.company_registry)]).mapped('id')
    #     if len(partner_id) > 0:
    #         partner_id = partner_id[0]
    #     else:
    #         raise Warning(_("No id found"))
    #     if something:
    #         view_type = "form"
    #         view_id = "view_partner_employer_form"
    #     return{
    #         'name': _('Employers'), #vad gör den?
    #         'domain':[('id', '=', partner_id)],
    #         'view_type': view_type,
    #         'res_model': 'res.partner',
    #         'view_id':  view_id,
    #         'view_mode': 'form',
    #         'type': 'ir.actions.act_window',
    #     }

class ResPartnerJobseekerSearchWizard(models.TransientModel):
    _name = "res.partner.jobseeker.search.wizard"

    #gdpr_id = fields.Many2one('gdpr.inventory') 
    #gdpr_reasons = fields.Many2one(related="gdpr_id.reasons?")
    search_reason = fields.Selection(string="Search reason",selection=[('registrera inkomna handlingar','Registrera inkomna handlingar'), ('uppföljning av arbetssökands planering','Uppföljning av arbetssökands planering'), ('registervård','Registervård'), ('matchning','Matchning'), ('beslut åt annan handläggare','Beslut åt annan handläggare'),('administration av rekryteringsträff/gruppaktivitet/projekt','Administration av rekryteringsträff/gruppaktivitet/projekt'),('utredning','Utredning'),('motringning','Motringning'),('annan orsak','Annan orsak')])#
    identification = fields.Selection(string="Identification",selection=[('id-handling','ID-Handling'), ('lma-kort/uppehållstillståndskort','LMA-kort/Uppehållstillståndskort'), ('känd (tidigare identifierad)','Känd (tidigare identifierad)'), ('identifierad genom intygsgivare','Identifierad genom intygsgivare'), ('kontrollfrågor','Kontrollfrågor'),('mobilt bankid','Mobilt BankID')])#
    search_domain = fields.Char(string="Search Filter", default=[('social_sec_nr', '=', '')] )

    @api.multi
    def search_jobseeker(self):
        raise Warning("Inte implementerat än")
        view_type = "tree"
        view_id = self.env.ref("partner_view_360.view_partner_jobseeker_form").id
        partner_id = self.env['res.partner'].search(safe_eval(self.search_domain)).mapped('id')
        if len(partner_id) == 1:
            partner_id = partner_id[0]
        elif len(partner_id) > 1:
            view_id = self.env.ref("partner_view_360.view_partner_jobseeker_kanban").id
        else:
            raise Warning(_("No id found"))
        return{
            'name': _('Jobseekers'),
            'domain':[('id', '=', partner_id)],
            #'view_type': 'tree',
            'res_model': 'res.partner',
            'view_id':  view_id,
            'view_mode': 'form',
            'type': 'ir.actions.act_window',
        }
    

