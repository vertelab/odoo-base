# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class WebsiteAnalyticsReportTypePreview(models.TransientModel):
    _name = 'website.analytics.report.type.preview'
    _description = 'Website Analytics Report Type Preview'

    report_type_id = fields.Many2one(
        'website.analytics.report.type',
        string='Report Type',
        required=True,
        readonly=True
    )

    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        required=True,
        domain="[('analytics_provider_id', '!=', False)]"
    )

    # period = fields.Selection([
    #     ('day', 'Day'),
    #     ('week', 'Week'),
    #     ('month', 'Month'),
    #     ('year', 'Year'),
    #     ('range', 'Range'),
    # ], string='Period', required=True)
    #
    # date = fields.Selection([
    #     ('today', 'Today'),
    #     ('yesterday', 'Yesterday'),
    #     ('lastWeek', 'Last Week'),
    #     ('lastMonth', 'Last Month'),
    #     ('lastYear', 'Last Year'),
    # ], string='Date', required=True)
    #
    # last_n = fields.Integer(
    #     string='Last N',
    #     help='Number of periods to show (e.g., last 30 days, last 12 weeks). Leave 0 to disable.',
    #     default=0
    # )

    # Preview result
    preview_image = fields.Binary(string='Preview', readonly=True)
    preview_generated = fields.Boolean(default=False)

    # @api.model
    # def default_get(self, fields_list):
    #     """Set default values from report type"""
    #     res = super().default_get(fields_list)
    #
    #     if self._context.get('default_report_type_id'):
    #         report_type = self.env['website.analytics.report.type'].browse(
    #             self._context['default_report_type_id']
    #         )
    #         res['period'] = report_type.period
    #         res['date'] = report_type.date
    #         res['last_n'] = report_type.last_n
    #
    #     return res

    def action_generate_preview(self):
        """Generate preview image"""
        self.ensure_one()

        if not self.partner_id.analytics_provider_id:
            raise UserError(_('Selected partner has no analytics provider configured.'))

        if not self.partner_id.analytics_site_id:
            raise UserError(_('Selected partner has no site ID configured.'))

        # Fetch the image using report type's configuration
        provider = self.partner_id.analytics_provider_id
        image_data = provider.fetch_report_image(self.partner_id, self.report_type_id)

        if not image_data:
            raise UserError(_('Failed to generate preview. Check logs for details.'))

        # Store as binary
        self.write({
            'preview_image': image_data,
            'preview_generated': True,
        })

        # Return to the wizard to show the image
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'website.analytics.report.type.preview',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }