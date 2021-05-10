from odoo import fields, models, api, _
from odoo.exceptions import Warning

class ResPartner(models.Model):

    _inherit = 'res.partner'

    search_partner_name = fields.Char("Search for name")

    def search_partner_by_name(self):
        self.ensure_one()
        if self.search_partner_name:
            name_upper = self.search_partner_name.upper()
            name_lower = self.search_partner_name.lower()
            name_title = self.search_partner_name.title()
            partners = self.env['res.partner'].search(
                ['|', '|', ('name', 'ilike', name_lower), ('name', 'ilike', name_upper),
                 ('name', 'ilike', name_title)])
            if partners:
                if len(partners) > 1:
                    self.search_partner_name = ''
                    kanban_view = self.env.ref('base.res_partner_kanban_view')
                    tree_view = self.env.ref('base.view_partner_tree')
                    form_view = self.env.ref('partner_design_mocukup.partner_view_from_search_partner')
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
                        'target': 'current',
                        'context': {'no_breadcrumbs': True},
                    }
                elif len(partners) == 1:
                    self.search_partner_name = ''
                    form_view = self.env.ref('partner_design_mocukup.partner_view_from_search_partner')
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
                        'context': {'no_breadcrumbs': True},
                    }
            else:
                raise Warning(_("No match found!"))
        else:
            raise Warning(_("Enter name in search box!"))
