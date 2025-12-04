# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import timedelta
from dateutil.relativedelta import relativedelta
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from io import BytesIO
import base64
import logging

_logger = logging.getLogger(__name__)


class SERPMixin(models.AbstractModel):
    _name = 'serp.mixin'
    _description = 'SERP Tracking Mixin'

    # Domain configuration
    serp_domain = fields.Char(
        string='SERP Domain',
        help='Domain to track (e.g., vertel.se)',
        required=True
    )

    # Tracking configuration
    serp_provider_id = fields.Many2one(
        'serp.provider',
        string='SERP Provider'
    )
    serp_keyword_ids = fields.Many2many('serp.keyword', string='Keywords')
    serp_country_ids = fields.Many2many('res.country', string='Countries')

    # Scheduling
    serp_interval_number = fields.Integer(string="Interval Number", default=1)
    serp_interval_type = fields.Selection([
        ('minutes', 'Minutes'),
        ('hours', 'Hours'),
        ('days', 'Days'),
        ('weeks', 'Weeks'),
        ('months', 'Months')
    ], string="Interval Type", default='days')
    serp_nextcall = fields.Datetime(string="Next Check")


    # Results
    serp_result_ids = fields.One2many(
        'serp.result',
        compute='_compute_serp_result_ids',
        string='SERP Results'
    )

    # Stats
    serp_last_check = fields.Datetime(string='Last SERP Check', readonly=True)
    serp_result_count = fields.Integer(
        string='Results Count',
        compute='_compute_serp_result_count',
        help='Total number of SERP results tracked'
    )

    serp_report_count = fields.Integer(
        string='SERP Report',
        compute='_compute_serp_report_count',
        help='Total number of SERP reports'
    )

    project_id = fields.Many2one('project.project', string="Project")

    @api.depends()
    def _compute_serp_result_ids(self):
        """Compute SERP results for this record"""
        for record in self:
            record.serp_result_ids = self.env['serp.result'].search([
                ('res_model', '=', record._name),
                ('res_id', '=', record.id)
            ])

    @api.depends()
    def _compute_serp_result_count(self):
        """Calculate total number of SERP results"""
        for record in self:
            record.serp_result_count = self.env['serp.result'].search_count([
                ('res_model', '=', record._name),
                ('res_id', '=', record.id)
            ])

    @api.depends('project_id')
    def _compute_serp_report_count(self):
        for rec in self:
            if rec.project_id:
                rec.serp_report_count = len(rec.project_id.task_ids)
            else:
                rec.serp_report_count = 0

    def _compute_nextcall(self):
        """Calculate next call time based on interval settings"""
        self.ensure_one()
        now = fields.Datetime.now()

        interval_map = {
            'minutes': timedelta(minutes=self.serp_interval_number),
            'hours': timedelta(hours=self.serp_interval_number),
            'days': timedelta(days=self.serp_interval_number),
            'weeks': timedelta(weeks=self.serp_interval_number),
            'months': timedelta(days=self.serp_interval_number * 30),
        }

        delta = interval_map.get(self.serp_interval_type, timedelta(days=1))
        return now + delta

    def _validate_serp_config(self):
        """Validate SERP configuration before running check"""
        self.ensure_one()

        if not self.serp_domain:
            raise UserError(_('Please set a domain to track'))
        if not self.serp_provider_id:
            raise UserError(_('Please select a SERP provider'))
        if not self.serp_keyword_ids:
            raise UserError(_('Please add keywords to track'))
        if not self.serp_country_ids:
            raise UserError(_('Please select at least one country'))

    def _execute_serp_search(self, keyword, country_code):
        """Execute a single SERP search and return results"""
        self.ensure_one()

        try:
            search_results = self.serp_provider_id.execute_search(
                keyword=keyword,
                domain=self.serp_domain,
                country=country_code,
                language='sv'  # Default for now
            )

            # Normalize to list format
            if isinstance(search_results, dict):
                search_results = [search_results]

            return search_results, None
        except Exception as e:
            return [], str(e)

    def _create_serp_results(self, search_results, keyword, country_code):
        """Create SERP result records from search results"""
        self.ensure_one()
        created_count = 0

        for search_result in search_results:
            if search_result.get('success') and search_result.get('position'):
                self.env['serp.result'].create({
                    'res_model': self._name,
                    'res_id': self.id,
                    'keyword': keyword,
                    'position': search_result['position'],
                    'url': search_result.get('url'),
                    'title': search_result.get('title'),
                    'snippet': search_result.get('snippet'),
                    'search_date': fields.Datetime.now(),
                    'provider_id': self.serp_provider_id.id,
                    'country_code': country_code,
                    'language': 'sv',
                    'search_engine': self.serp_provider_id.search_engine,
                })
                created_count += 1

        return created_count

    def _process_serp_check(self):
        """Core logic for SERP checking - reusable by both manual and cron"""
        self.ensure_one()
        self._validate_serp_config()

        keywords = self.serp_keyword_ids.mapped('name')
        countries = self.serp_country_ids.mapped('code')

        results_created = 0
        errors = []

        for country_code in countries:
            for keyword in keywords:
                search_results, error = self._execute_serp_search(keyword, country_code)

                if error:
                    errors.append(f"{keyword} ({country_code}): {error}")
                    continue

                created = self._create_serp_results(search_results, keyword, country_code)
                results_created += created

        # Update tracking fields
        self.write({
            'serp_last_check': fields.Datetime.now(),
            'serp_nextcall': self._compute_nextcall()
        })

        # Auto-generate report after SERP check
        if results_created > 0:
            try:
                self._auto_generate_report()
            except Exception as e:
                _logger.error(f"Failed to auto-generate report: {str(e)}")
                errors.append(f"Report generation failed: {str(e)}")

        return results_created, errors

    def _auto_generate_report(self):
        """Automatically generate a report after SERP check"""
        self.ensure_one()

        # Ensure project exists
        if not self.project_id:
            self.project_id = self.env['project.project'].create({
                'name': f'SERP Reports - {self.display_name}',
                'partner_id': self.id if self._name == 'res.partner' else False,
            })

        # Get date range (last 30 days)
        date_to = fields.Date.today()
        date_from = date_to - relativedelta(days=30)
        # date_from = fields.Date.today()

        # Get results
        results = self.env['serp.result'].search([
            ('res_model', '=', self._name),
            ('res_id', '=', self.id),
            ('search_date', '>=', date_from),
            ('search_date', '<=', date_to),
        ], order='search_date asc')

        if not results:
            _logger.info(f"No results to generate report for {self.display_name}")
            return

        # Generate graph
        graph_image = self._generate_report_graph(results)

        # Build description
        description_html = f'''
        <img src="data:image/png;base64,{graph_image}" style="max-width: 100%; height: auto;"/>

        <h3>Summary</h3>
        <ul>
            <li><strong>Total Results:</strong> {len(results)}</li>
            <li><strong>Keywords Tracked:</strong> {', '.join(results.mapped('keyword'))}</li>
            <li><strong>Date Range:</strong> {date_from} to {date_to}</li>
        </ul>
        '''

        # Create task
        task = self.env['project.task'].create({
            'name': f'SERP Report - {self.display_name} ({date_from} to {date_to})',
            'project_id': self.project_id.id,
            'partner_id': self.id if self._name == 'res.partner' else False,
            'description': description_html,
        })

        _logger.info(f"Created SERP report task {task.id}")
        return task

    def _generate_report_graph(self, results):
        """Generate matplotlib graph and return base64 image"""
        keywords = sorted(list(set(results.mapped('keyword'))))

        fig, ax = plt.subplots(figsize=(12, 6))

        for keyword in keywords:
            keyword_results = results.filtered(lambda r: r.keyword == keyword).sorted('search_date')
            if not keyword_results:
                continue

            dates = [d.date() if hasattr(d, 'date') else d for d in keyword_results.mapped('search_date')]
            positions = keyword_results.mapped('position')
            ax.plot(dates, positions, marker='o', linewidth=2, markersize=8, label=keyword)

        ax.invert_yaxis()
        ax.set_xlabel('Date', fontsize=12, fontweight='bold')
        ax.set_ylabel('Position', fontsize=12, fontweight='bold')
        ax.set_title(f'SERP Position Tracking - {self.display_name}', fontsize=14, fontweight='bold', pad=20)
        ax.grid(True, alpha=0.3)
        ax.legend(loc='best', frameon=True, shadow=True)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        fig.autofmt_xdate()
        ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
        plt.tight_layout()

        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close(fig)

        return image_base64

    def action_check_serp(self):
        """Manually trigger SERP check - shows notification"""
        self.ensure_one()

        results_created, errors = self._process_serp_check()

        # Build notification message
        if results_created:
            message = _('%s results found and saved') % results_created
        else:
            message = _('No results found')

        if errors:
            message += _('\n\nErrors:\n%s') % '\n'.join(errors)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('SERP Check Complete'),
                'message': message,
                'type': 'success' if results_created else 'warning',
                'sticky': bool(errors),
            }
        }

    @api.model
    def _cron_check_serp(self):
        """Cron job to check SERP for scheduled records"""
        now = fields.Datetime.now()

        # Find records ready for checking
        records = self.search([
            ('serp_domain', '!=', False),
            ('serp_provider_id', '!=', False),
            ('serp_keyword_ids', '!=', False),
            ('serp_country_ids', '!=', False),
            '|',
            ('serp_nextcall', '=', False),
            ('serp_nextcall', '<=', now)
        ])

        _logger.info(f"SERP Cron: Found {len(records)} records to check")

        for record in records:
            try:
                results_created, errors = record._process_serp_check()

                if errors:
                    _logger.warning(
                        f"SERP check completed with errors for {record._name} {record.id}: "
                        f"{results_created} results created, {len(errors)} errors"
                    )
                else:
                    _logger.info(
                        f"SERP check successful for {record._name} {record.id}: "
                        f"{results_created} results created"
                    )

            except Exception as e:
                _logger.error(
                    f"SERP check failed for {record._name} {record.id}: {str(e)}",
                    exc_info=True
                )

    def action_view_reports(self):
        self.ensure_one()
        return {
            'name': _('SERP Report'),
            'view_mode': 'kanban,form',
            'res_model': 'project.task',
            'domain': [('project_id', '=', self.project_id.id)],
            'type': 'ir.actions.act_window',
        }