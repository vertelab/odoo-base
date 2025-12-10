# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from markupsafe import Markup
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

    # Tracking configuration
    serp_provider_id = fields.Many2one('serp.provider', string='SERP Provider')

    # SERP Scheduling
    serp_interval_number = fields.Integer(string="Check Interval", default=1)
    serp_interval_type = fields.Selection([
        ('minutes', 'Minutes'),
        ('hours', 'Hours'),
        ('days', 'Days'),
        ('weeks', 'Weeks'),
        ('months', 'Months')
    ], string="Check Interval Type", default='days')
    serp_nextcall = fields.Datetime(string="Next SERP Check")

    # Report Scheduling
    report_interval_number = fields.Integer(string="Report Interval", default=7)
    report_interval_type = fields.Selection([
        ('minutes', 'Minutes'),
        ('hours', 'Hours'),
        ('days', 'Days'),
        ('weeks', 'Weeks'),
        ('months', 'Months')
    ], string="Report Interval Type", default='days')
    report_nextcall = fields.Datetime(string="Next Report Generation")

    # Date Range
    date_from = fields.Date(
        string='From Date',
        required=True,
        default=lambda self: self._default_date_from()
    )
    date_to = fields.Date(
        string='To Date',
        required=True,
        default=lambda self: self._default_date_to()
    )

    # Results
    serp_result_ids = fields.One2many(
        'serp.result',
        compute='_compute_serp_result_ids',
        string='SERP Results'
    )
    serp_last_check = fields.Datetime(string='Last SERP Check', readonly=True)
    serp_result_count = fields.Integer(
        string='Results Count',
        compute='_compute_serp_result_count',
        help='Total number of SERP results tracked'
    )
    serp_report_count = fields.Integer(
        string='SERP Reports',
        compute='_compute_serp_report_count',
        help='Total number of SERP reports'
    )

    serp_report_template_id = fields.Many2one(
        'ir.ui.view',
        string="SERP Report Template",
        domain="[('type', '=', 'qweb')]",
        default=lambda self: self._get_default_serp_template(),
    )

    # Project for reports
    project_id = fields.Many2one('project.project', string="Project")

    # Website Analytics
    analytics_provider_id = fields.Many2one('website.analytics.provider', string='Analytics Provider')
    analytics_site_id = fields.Char(string='Site ID', help='The site/property ID in the analytics platform')
    analytics_last_sync = fields.Datetime(string='Last Sync', readonly=True)
    analytics_report_template_id = fields.Many2one(
        'ir.ui.view',
        string="Analytics Template",
        domain="[('type', '=', 'qweb')]",
        default=lambda self: self._get_default_analytics_template(),
    )


    # analytics_report_type_ids = fields.Many2many(
    #     'website.analytics.report.type',
    #     string='Reports to Generate',
    #     help='Select which reports/graphs to generate'
    # )

    # -------------------------------------------------------------------------
    # DEFAULTS
    # -------------------------------------------------------------------------

    def _default_date_from(self):
        return date.today().replace(day=1)

    def _default_date_to(self):
        today = date.today()
        next_month = today.replace(day=28) + relativedelta(days=4)
        return next_month.replace(day=1) - relativedelta(days=1)

    @api.model
    def _get_default_serp_template(self):
        return self.env.ref('base_serp.serp_keywords_template', raise_if_not_found=False)

    @api.model
    def _get_default_analytics_template(self):
        return self.env.ref('base_serp.analytics_template', raise_if_not_found=False)

    # -------------------------------------------------------------------------
    # COMPUTE METHODS
    # -------------------------------------------------------------------------

    @api.depends()
    def _compute_serp_result_ids(self):
        for record in self:
            record.serp_result_ids = self.env['serp.result'].search([
                ('res_model', '=', record._name),
                ('res_id', '=', record.id)
            ])

    @api.depends()
    def _compute_serp_result_count(self):
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

    # -------------------------------------------------------------------------
    # SCHEDULING HELPERS
    # -------------------------------------------------------------------------

    def _compute_nextcall(self):
        self.ensure_one()
        now = fields.Datetime.now()

        interval_map = {
            'minutes': timedelta(minutes=self.serp_interval_number),
            'hours': timedelta(hours=self.serp_interval_number),
            'days': timedelta(days=self.serp_interval_number),
            'weeks': timedelta(weeks=self.serp_interval_number),
            'months': relativedelta(months=self.serp_interval_number),
        }

        delta = interval_map.get(self.serp_interval_type, timedelta(days=1))
        return now + delta

    def _compute_report_nextcall(self):
        self.ensure_one()
        now = fields.Datetime.now()

        interval_map = {
            'minutes': timedelta(minutes=self.report_interval_number),
            'hours': timedelta(hours=self.report_interval_number),
            'days': timedelta(days=self.report_interval_number),
            'weeks': timedelta(weeks=self.report_interval_number),
            'months': relativedelta(months=self.report_interval_number),
        }

        delta = interval_map.get(self.report_interval_type, timedelta(days=7))
        return now + delta

    # -------------------------------------------------------------------------
    # SERP CHECK LOGIC
    # -------------------------------------------------------------------------

    def _validate_serp_config(self):
        self.ensure_one()

        if not self.website:
            raise UserError(_('Please set a website URL'))
        if not self.serp_provider_id:
            raise UserError(_('Please select a SERP provider'))
        if not self.serp_keyword_ids:
            raise UserError(_('Please add keywords to track'))

        keywords_without_country = self.serp_keyword_ids.filtered(lambda k: not k.country_id)
        if keywords_without_country:
            raise UserError(_('All keywords must have a country selected'))

    def _execute_serp_search(self, keyword, country_code, language='sv'):
        self.ensure_one()

        try:
            search_results = self.serp_provider_id.execute_search(
                keyword=keyword,
                domain=self.website,
                country=country_code,
                language=language
            )

            if isinstance(search_results, dict):
                search_results = [search_results]

            return search_results, None
        except Exception as e:
            return [], str(e)

    def _create_serp_results(self, search_results, keyword, country_code, language):
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
                    'language': language,
                    'search_engine': self.serp_provider_id.search_engine,
                })
                created_count += 1

        return created_count

    def _process_serp_check(self):
        self.ensure_one()
        self._validate_serp_config()

        results_created = 0
        errors = []

        for keyword_record in self.serp_keyword_ids:
            keyword = keyword_record.keyword
            country_code = keyword_record.country_id.code
            language = keyword_record.language_id.iso_code

            search_results, error = self._execute_serp_search(keyword, country_code, language)

            if error:
                errors.append(f"{keyword} ({country_code}): {error}")
                continue

            created = self._create_serp_results(search_results, keyword, country_code, language)
            results_created += created

        self.write({
            'serp_last_check': fields.Datetime.now(),
            'serp_nextcall': self._compute_nextcall()
        })

        return results_created, errors

    # -------------------------------------------------------------------------
    # REPORT GENERATION
    # -------------------------------------------------------------------------

    def _auto_generate_report(self, date_from=None, date_to=None):
        self.ensure_one()

        effective_date_from = date_from or self.date_from
        effective_date_to = date_to or self.date_to

        # Ensure project exists
        if not self.project_id:
            self.project_id = self.env['project.project'].create({
                'name': f'SERP Reports - {self.display_name}',
                'partner_id': self.id if self._name == 'res.partner' else False,
            })

        # Get results
        results = self.env['serp.result'].search([
            ('res_model', '=', self._name),
            ('res_id', '=', self.id),
            ('search_date', '>=', effective_date_from),
            ('search_date', '<=', effective_date_to),
        ], order='search_date asc')

        if not results:
            _logger.info(f"No results to generate report for {self.display_name} in the given date range.")
            return

        # Prepare data for template
        graph_image = self._generate_report_graph(results)
        keywords_data = self._prepare_keywords_data(results)
        # analytics_reports = self._fetch_analytics_reports_data()

        # Render template
        description_html = self.env['mail.render.mixin']._render_template(
            'base_serp.serp_report_content',
            'res.partner',
            self.ids,
            engine='qweb_view',
            add_context={
                'graph_image': graph_image,
                'keywords_data': keywords_data,
                'total_results': len(results),
                'keywords_list': ', '.join(set(results.mapped('keyword'))),
                'date_from': str(effective_date_from),
                'date_to': str(effective_date_to),
                'object': self,
                # 'analytics_reports': analytics_reports,
            },
            options={
                'preserve_comments': True,
                'post_process': True,
            },
        )[self.id]

        # Create task
        task = self.env['project.task'].create({
            'name': f'SERP Report - {self.display_name} ({effective_date_from} to {effective_date_to})',
            'project_id': self.project_id.id,
            'partner_id': self.id if self._name == 'res.partner' else False,
            'description': description_html,
        })

        _logger.info(f"Created SERP report task {task.id}")
        return task

    def _prepare_keywords_data(self, results):
        all_keywords = sorted(list(set(self.serp_keyword_ids.mapped('keyword'))))
        keywords_data = []

        for keyword in all_keywords:
            keyword_results = results.filtered(lambda r: r.keyword == keyword).sorted('search_date')

            if keyword_results:
                # Has results
                first_position = keyword_results[0].position
                last_position = keyword_results[-1].position
                position_change = first_position - last_position

                if position_change > 0:
                    change_icon = '📈'
                    change_class = 'green'
                    change_text = f'+{position_change}'
                elif position_change < 0:
                    change_icon = '📉'
                    change_class = 'red'
                    change_text = f'{position_change}'
                else:
                    change_icon = '➡️'
                    change_class = 'gray'
                    change_text = '0'

                keywords_data.append({
                    'keyword': keyword,
                    'first_position': first_position,
                    'last_position': last_position,
                    'change_icon': change_icon,
                    'change_class': change_class,
                    'change_text': change_text,
                    'has_data': True,
                })
            else:
                # No results yet
                keywords_data.append({
                    'keyword': keyword,
                    'first_position': '-',
                    'last_position': '-',
                    'change_icon': '',
                    'change_class': 'gray',
                    'change_text': 'No data',
                    'has_data': False,
                })

        return keywords_data

    def _generate_report_graph(self, results):
        all_keywords = sorted(list(set(self.serp_keyword_ids.mapped('keyword'))))

        fig, ax = plt.subplots(figsize=(12, 6))

        for keyword in all_keywords:
            keyword_results = results.filtered(lambda r: r.keyword == keyword).sorted('search_date')

            if not keyword_results:
                # Skip keywords with no data in graph
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

    def _fetch_analytics_reports_data(self):
        self.ensure_one()

        if not self.analytics_report_type_ids:
            return []

        reports_data = []
        for report_type in self.analytics_report_type_ids:
            try:
                image_data = self.analytics_provider_id.fetch_report_image(self, report_type)
                reports_data.append({
                    'name': report_type.name,
                    'image_data': image_data if image_data else None,
                })
            except Exception as e:
                _logger.error(f"Failed to fetch {report_type.name}: {e}")
                reports_data.append({
                    'name': report_type.name,
                    'image_data': None,
                })

        return reports_data



    # -------------------------------------------------------------------------
    # ACTIONS
    # -------------------------------------------------------------------------

    def action_check_serp(self):
        self.ensure_one()

        results_created, errors = self._process_serp_check()

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

    def action_view_reports(self):
        self.ensure_one()
        return {
            'name': _('SERP Reports'),
            'view_mode': 'kanban,form',
            'res_model': 'project.task',
            'domain': [('project_id', '=', self.project_id.id)],
            'type': 'ir.actions.act_window',
        }

    # -------------------------------------------------------------------------
    # CRON JOBS
    # -------------------------------------------------------------------------

    @api.model
    def _cron_check_serp(self):
        now = fields.Datetime.now()

        records = self.search([
            ('website', '!=', False),
            ('serp_provider_id', '!=', False),
            ('serp_keyword_ids', '!=', False),
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

    @api.model
    def _cron_generate_serp_report(self):
        now = fields.Datetime.now()

        records = self.search([
            ('website', '!=', False),
            ('serp_provider_id', '!=', False),
            ('serp_keyword_ids', '!=', False),
            '|',
            ('report_nextcall', '=', False),
            ('report_nextcall', '<=', now)
        ])

        _logger.info(f"SERP Report Cron: Found {len(records)} records to generate reports")

        for record in records:
            try:
                record._auto_generate_report(date_from=record.date_from, date_to=record.date_to)
                record.write({'report_nextcall': record._compute_report_nextcall()})
                _logger.info(f"SERP report generated for {record._name} {record.id}")

            except Exception as e:
                _logger.error(
                    f"SERP report generation failed for {record._name} {record.id}: {str(e)}",
                    exc_info=True
                )