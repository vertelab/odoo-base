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


    # Preview result
    preview_image = fields.Binary(string='Preview', readonly=True)
    preview_generated = fields.Boolean(default=False)

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