from odoo import fields, models, api, _
from odoo.exceptions import Warning

class ResPartner(models.Model):

    _inherit = 'res.partner'

    search_partner_name = fields.Char("Search for name")
    links = fields.Html("Links", compute='_compute_links')

    @api.multi
    def _compute_links(self):
        links = self.env["partner.links"].search(
            [
                "|",
                ("group_ids", "=", False),
                ("group_ids", "in", self.env.user.groups_id.ids),
            ]
        )
        if links:
            for partner in self:
                if partner.social_sec_nr:
                    data = links.get_links(partner)
                    html_data = "<table>"
                    for link in data:
                        html_data += "<tr><td><img height='25px' width='25px' src='%(icon)s'/>  " \
                                     "<a href='%(url)s' target='_blank'> %(name)s </a></td></tr>" % \
                                     {'icon': link.get('icon'), 'url': link.get('url'), 'name': link.get('name')}
                    html_data += "</table>"
                    partner.links = html_data

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if 'from_advance_search' in self._context and len(args) == 0:
            args = ['id', '=', 0]
        if 'from_advance_search' in self._context and ['id', '=', 0] in args and len(args) > 1:
            args.remove(['id', '=', 0])
        result = super(ResPartner, self).search(args, offset=offset, limit=False, order=order, count=count)
        return result

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        res = super(ResPartner, self).search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order)
        return res

    def advance_search_partner(self):
        self.ensure_one()
        kanban_view = self.env.ref('base.res_partner_kanban_view')
        tree_view = self.env.ref('base.view_partner_tree')
        form_view = self.env.ref('partner_design_mockup.partner_view_from_advance_search_partner')
        return {
            'name': _('Contacts'),
            'view_type': 'form',
            'view_mode': 'kanban,tree,form',
            'res_model': 'res.partner',
            'views': [
                (kanban_view.id, 'kanban'),
                (tree_view.id, 'tree'),
                (form_view.id, 'form')
            ],
            'type': 'ir.actions.act_window',
            'domain': [('id', '=', 0)],
            'target': 'current',
            'context': {'no_breadcrumbs': True,
                        'from_advance_search': True},
        }

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
                    form_view = self.env.ref('partner_design_mockup.partner_view_from_search_partner')
                    return {
                        'name': _('Contacts'),
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
                        'context': {'no_breadcrumbs': True},
                    }
            else:
                raise Warning(_("No match found!"))
        else:
            raise Warning(_("Enter name in search box!"))
