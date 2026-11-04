# -*- coding: utf-8 -*-
import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ForetagssokSimilarWizard(models.TransientModel):
    _name = 'foretagssok.similar.wizard'
    _description = 'Find Similar Companies by SNI'

    partner_id = fields.Many2one('res.partner', string='Partner', required=True)
    sni_code = fields.Char(string='SNI Code', required=True)
    sni_name = fields.Char(string='SNI Description')
    city = fields.Char(string='City')
    min_revenue = fields.Float(string='Min Revenue')
    max_revenue = fields.Float(string='Max Revenue')
    has_annual_report = fields.Boolean(string='Has Digital Annual Report')
    exact_only = fields.Boolean(
        string='Exact Figures Only',
        help='Only include companies with exact figures from digital annual reports.',
    )
    sort_by = fields.Selection(
        selection=[
            ('revenue_desc', 'Revenue (high to low)'),
            ('revenue_asc', 'Revenue (low to high)'),
            ('name_asc', 'Name (A-Z)'),
            ('name_desc', 'Name (Z-A)'),
        ],
        string='Sort By',
        default='revenue_desc',
    )
    limit = fields.Integer(string='Limit', default=50)
    line_ids = fields.One2many(
        'foretagssok.similar.wizard.line',
        'wizard_id',
        string='Results',
    )

    def action_search(self):
        self.ensure_one()
        Partner = self.env['res.partner']
        try:
            companies = Partner._foretagsapi_search_by_sni(
                self.sni_code,
                city=self.city or None,
                min_revenue=self.min_revenue or None,
                max_revenue=self.max_revenue or None,
                has_annual_report=self.has_annual_report or None,
                exact_only=self.exact_only or None,
                sort_by=self.sort_by or None,
                limit=self.limit,
            )
        except UserError as e:
            raise UserError(_(
                'Could not search for similar companies. The API may require a city filter for large SNI branches.\n\n%s'
            ) % e)

        self.line_ids.unlink()
        lines = []
        for company in companies:
            org_number = Partner._foretagsapi_format_org_number(company.get('orgNumber'))
            # Skip the current partner
            if self.partner_id.company_registry and org_number == self.partner_id.company_registry:
                continue
            address = company.get('postalAddress') or {}
            lines.append((0, 0, {
                'wizard_id': self.id,
                'name': company.get('name'),
                'org_number': org_number,
                'street': address.get('street'),
                'postal_code': address.get('postalCode'),
                'city': address.get('city'),
                'business_description': company.get('businessDescription'),
                'raw_data': str(company),
            }))
        self.write({'line_ids': lines})
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_create_partners(self):
        self.ensure_one()
        created = self.env['res.partner']
        for line in self.line_ids.filtered('selected'):
            partner = self.env['res.partner'].create({
                'name': line.name,
                'company_type': 'company',
                'company_registry': line.org_number,
                'street': line.street,
                'zip': line.postal_code,
                'city': line.city,
            })
            created |= partner
        if not created:
            raise UserError(_('No rows were selected.'))
        return {
            'type': 'ir.actions.act_window',
            'name': _('Created Partners'),
            'res_model': 'res.partner',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', created.ids)],
        }


class ForetagssokSimilarWizardLine(models.TransientModel):
    _name = 'foretagssok.similar.wizard.line'
    _description = 'Similar Company Search Result'

    wizard_id = fields.Many2one(
        'foretagssok.similar.wizard',
        string='Wizard',
        required=True,
        ondelete='cascade',
    )
    selected = fields.Boolean(string='Select', default=False)
    name = fields.Char(string='Company Name', readonly=True)
    org_number = fields.Char(string='Org. Number', readonly=True)
    street = fields.Char(string='Street', readonly=True)
    postal_code = fields.Char(string='Postal Code', readonly=True)
    city = fields.Char(string='City', readonly=True)
    business_description = fields.Text(string='Business Description', readonly=True)
    raw_data = fields.Text(string='Raw Data', readonly=True)
