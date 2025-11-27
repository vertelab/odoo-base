# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SERPMixin(models.AbstractModel):
    _name = 'serp.mixin'
    _description = 'SERP Tracking Mixin'

    # Domain configuration
    serp_domain = fields.Char(
        string='SERP Domain',
        help='Domain to track (e.g., vertel.se)'
    )

    # Tracking configuration
    serp_provider_id = fields.Many2one(
        'serp.provider',
        string='SERP Provider'
    )

    serp_keywords = fields.Char(string='Keywords', help='Comma-separated keywords')

    serp_country_code = fields.Char(
        string='Country Code',
        default='SE',
        help='Country code for search (e.g., SE, US, GB)'
    )

    serp_language = fields.Selection(
        selection=[
            ('sv', 'Swedish'),
            ('en', 'English'),
        ],
        string='Language',
        default='sv',
        help='Search language'
    )

    serp_result_ids = fields.One2many(
        'serp.result',
        compute='_compute_serp_result_ids',
        string='SERP Results'
    )

    # Computed/Stats
    serp_last_check = fields.Datetime(
        string='Last SERP Check',
        readonly=True
    )
    serp_avg_position = fields.Float(
        string='Average Position',
        compute='_compute_serp_stats',
        help='Average ranking position across all keywords'
    )
    serp_result_count = fields.Integer(
        string='Keywords Tracked',
        compute='_compute_serp_stats'
    )

    @api.depends()
    def _compute_serp_result_ids(self):
        """Compute SERP results for this record"""
        for record in self:
            record.serp_result_ids = self.env['serp.result'].search([
                ('res_model', '=', record._name),
                ('res_id', '=', record.id)
            ])

    @api.depends('serp_result_ids.position')
    def _compute_serp_stats(self):
        """Calculate SERP statistics"""
        for record in self:
            results = record.serp_result_ids

            # Count results
            record.serp_result_count = len(results)

            # Calculate average position
            if results:
                record.serp_avg_position = sum(results.mapped('position')) / len(results)
            else:
                record.serp_avg_position = 0.0

    def action_check_serp(self):
        """Manually trigger SERP check for this record"""
        self.ensure_one()

        # Validations
        if not self.serp_provider_id:
            raise UserError(_('Please select a SERP provider'))

        if not self.serp_keywords:
            raise UserError(_('Please add keywords to track'))

        # Parse keywords (comma-separated)
        keywords = [k.strip() for k in self.serp_keywords.split(',') if k.strip()]

        if not keywords:
            raise UserError(_('No valid keywords found'))

        # Execute search for each keyword
        results_created = 0
        errors = []

        for keyword in keywords:
            try:
                # Execute search via provider
                search_results = self.serp_provider_id.execute_search(
                    keyword=keyword,
                    domain=self.serp_domain or None,  # ← Can be None now
                    country=self.serp_country_code or 'SE',
                    language=self.serp_language or 'sv'
                )

                # Handle both old format (single dict) and new format (list)
                if isinstance(search_results, dict):
                    search_results = [search_results]

                # Create result records for ALL matches
                for search_result in search_results:
                    if search_result.get('success') and search_result.get('position'):
                        self.env['serp.result'].create({
                            'res_model': self._name,
                            'res_id': self.id,
                            'keyword': keyword,
                            'domain': search_result.get('domain'),  # ← Use domain from result
                            'position': search_result['position'],
                            'url': search_result.get('url'),
                            'title': search_result.get('title'),
                            'snippet': search_result.get('snippet'),
                            'search_date': fields.Datetime.now(),
                            'provider_id': self.serp_provider_id.id,
                            'country_code': self.serp_country_code,
                            'language': self.serp_language,
                            'search_engine': self.serp_provider_id.search_engine,
                        })
                        results_created += 1

            except Exception as e:
                errors.append(f"{keyword}: {str(e)}")

        # Update last check time
        self.write({'serp_last_check': fields.Datetime.now()})

        # Show notification
        if results_created > 0:
            message = _('%s results found and saved') % results_created
            if errors:
                message += _('\n\nErrors: %s') % '\n'.join(errors)

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('SERP Check Complete'),
                    'message': message,
                    'type': 'success',
                    'sticky': False,
                }
            }
        else:
            message = _('No results found')
            if errors:
                message += _('\n\nErrors: %s') % '\n'.join(errors)

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('SERP Check Complete'),
                    'message': message,
                    'type': 'warning',
                    'sticky': True,
                }
            }