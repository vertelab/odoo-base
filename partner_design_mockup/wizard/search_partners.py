from odoo import fields, models, api,_
from odoo.exceptions import Warning

class SearchPartners(models.TransientModel):

    _name = 'search.partners'
    _description = "Seach Partners"

    search_partner = fields.Char("Search")
    name = fields.Boolean("Name", default=True)
    email = fields.Boolean("Email")
    no_match = fields.Boolean("No match found")

    def search_partners(self):
        self.ensure_one()
        context = self._context
        partners = []
        if self.search_partner and self.name and not self.email:
            name_upper = self.search_partner.upper()
            name_lower = self.search_partner.lower()
            name_title = self.search_partner.title()
            partners = self.env['res.partner'].search(['|', '|', ('name', 'ilike', name_lower), ('name', 'ilike', name_upper),
                                                       ('name', 'ilike', name_title)])
        elif self.search_partner and self.email and not self.name:
            partners = self.env['res.partner'].search([('email', 'ilike', self.search_partner)])
        elif self.search_partner and self.email and self.name:
            name_upper = self.search_partner.upper()
            name_lower = self.search_partner.lower()
            name_title = self.search_partner.title()
            partners = self.env['res.partner'].search(['|', '|', '|', ('name', 'ilike', name_lower),
            ('name', 'ilike', name_upper), ('name', 'ilike', name_title), ('email', 'ilike', self.search_partner)])
        elif not self.search_partner or not self.name or not self.email:
            raise Warning(_("Please add serach text with Criteria!"))
        if partners:
            if len(partners) > 1:
                self.no_match = False
                kanban_view = self.env.ref('base.res_partner_kanban_view')
                tree_view = self.env.ref('base.view_partner_tree')
                if 'from_advance_search_partner' in context:
                    form_view = self.env.ref('partner_design_mockup.partner_view_from_advance_search_partner')
                else:
                    form_view = self.env.ref('partner_design_mockup.partner_view_from_search_partner')
                return {
                    'name': _('Partners'),
                    'view_type': 'form',
                    'view_mode': 'kanban,tree,form',
                    'res_model': 'res.partner',
                    'views': [
                        (kanban_view.id, 'kanban'),
                        (tree_view.id, 'tree'),
                        (form_view.id, 'form')
                    ],
                    'type': 'ir.actions.act_window',
                    'domain': [('id', 'in', partners.ids)],
                    'target': 'current'
                }
            elif len(partners) == 1:
                self.no_match = False
                if 'from_advance_search_partner' in context:
                    form_view = self.env.ref('partner_design_mockup.partner_view_from_advance_search_partner')
                else:
                    form_view = self.env.ref('partner_design_mockup.partner_view_from_search_partner')
                return {
                    'name': partners.name,
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'res.partner',
                    'views': [(form_view.id, 'form')],
                    'view_id': form_view.id,
                    'target': 'current',
                    'res_id': partners.id,
                }
        else:
            self.no_match = True

