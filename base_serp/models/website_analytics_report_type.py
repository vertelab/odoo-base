# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import uuid


class WebsiteAnalyticsReportType(models.Model):
    _name = 'website.analytics.report.type'
    _description = 'Website Analytics Report Type Configuration'

    def _generate_report_type_id(self):
        return uuid.uuid4().hex[:8]

    name = fields.Char(string='Report Name', required=True)
    report_type_id = fields.Char(
        string='Report Type ID',
        required=True,
        readonly=True,
        copy=False,
        default=_generate_report_type_id
    )
    analytics_provider_id = fields.Many2one('website.analytics.provider', string='Analytics Provider')

    _sql_constraints = [
        ('report_type_id_uniq', 'unique(report_type_id)', 'Report Type ID must be unique!')
    ]

    def action_preview_report(self):
        self.ensure_one()

        return {
            'name': _('Preview Report'),
            'type': 'ir.actions.act_window',
            'res_model': 'website.analytics.report.type.preview',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_report_type_id': self.id,
            }
        }