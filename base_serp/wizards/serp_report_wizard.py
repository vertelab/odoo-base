# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)


class SerpReportWizard(models.TransientModel):
    _name = 'serp.report.wizard'
    _description = 'SERP Report Wizard'

    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        required=True,
        readonly=True,
        default=lambda self: self.env.context.get('active_id')
    )

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

    def _default_date_from(self):
        """First day of current month"""
        return date.today().replace(day=1)

    def _default_date_to(self):
        """Last day of current month"""
        today = date.today()
        next_month = today.replace(day=28) + relativedelta(days=4)
        return next_month.replace(day=1) - relativedelta(days=1)

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        """Validate date range"""
        for wizard in self:
            if wizard.date_from > wizard.date_to:
                raise UserError(_('From Date must be before To Date'))

    def action_generate_report(self):
        """Generate the SERP report and create project task"""
        self.ensure_one()

        if not self.partner_id.project_id:
            raise UserError(_(f"{self.partner_id.name} has no project."))

        # Build domain for filtering results
        domain = [
            ('res_model', '=', 'res.partner'),
            ('res_id', '=', self.partner_id.id),
            ('search_date', '>=', self.date_from),
            ('search_date', '<=', self.date_to),
        ]

        # Get results
        results = self.env['serp.result'].search(domain, order='search_date asc')

        if not results:
            raise UserError(_('No SERP results found for the selected date range'))

        try:
            # Use partner's method to generate graph (reusing mixin code)
            graph_image = self.partner_id._generate_report_graph(results)

            # Build HTML description
            description_html = f'''
            <img src="data:image/png;base64,{graph_image}" style="max-width: 100%; height: auto;"/>

            <h3>Summary</h3>
            <ul>
                <li><strong>Total Results:</strong> {len(results)}</li>
                <li><strong>Keywords Tracked:</strong> {', '.join(results.mapped('keyword'))}</li>
                <li><strong>Date Range:</strong> {self.date_from} to {self.date_to}</li>
            </ul>
            '''

            # Create project task
            task = self.env['project.task'].create({
                'name': f'SERP Report - {self.partner_id.name} ({self.date_from} to {self.date_to})',
                'partner_id': self.partner_id.id,
                'description': description_html,
                'project_id': self.partner_id.project_id.id
            })

            return {
                'type': 'ir.actions.act_window',
                'res_model': 'project.task',
                'res_id': task.id,
                'view_mode': 'form',
                'target': 'current',
            }

        except Exception as e:
            _logger.error(f"Error generating SERP report: {str(e)}")
            raise UserError(_('Error generating report: %s') % str(e))