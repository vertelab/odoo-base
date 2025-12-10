# -*- coding: utf-8 -*-

from odoo import models, fields, api


class WebsiteAnalyticsProvider(models.Model):
    _name = 'website.analytics.provider'
    _description = 'Analytics Provider'

    name = fields.Char(required=True)
    provider_type = fields.Selection(
        selection='_get_provider_types',
        required=True
    )
    base_url = fields.Char(string='Base URL', required=True, help='e.g., https://analytics.example.com')
    token_auth = fields.Char(string='API Token', required=True)
    active = fields.Boolean(default=True)

    @api.model
    def _get_provider_types(self):
        return []

    def fetch_analytics(self, resource):
        method_name = f'_fetch_{self.provider_type}_analytics'
        if hasattr(self, method_name):
            return getattr(self, method_name)(resource)
        else:
            raise NotImplementedError(f'Provider type {self.provider_type} not implemented')

    def fetch_site_summary(self, resource):
        method_name = f'_fetch_{self.provider_type}_site_summary'
        if hasattr(self, method_name):
            return getattr(self, method_name)(resource)
        else:
            raise NotImplementedError(f'Site summary for {self.provider_type} not implemented')

    def fetch_page_metrics(self, resource):
        method_name = f'_fetch_{self.provider_type}_page_metrics'
        if hasattr(self, method_name):
            return getattr(self, method_name)(resource)
        else:
            raise NotImplementedError(f'Page metrics for {self.provider_type} not implemented')

    def fetch_traffic_sources(self, resource):
        method_name = f'_fetch_{self.provider_type}_traffic_sources'
        if hasattr(self, method_name):
            return getattr(self, method_name)(resource)
        else:
            raise NotImplementedError(f'Traffic sources for {self.provider_type} not implemented')

    def fetch_report_image(self, resource, report_type):
        method_name = f'_fetch_{self.provider_type}_report_image'
        if hasattr(self, method_name):
            return getattr(self, method_name)(resource, report_type)
        else:
            raise NotImplementedError(f'Report image for {self.provider_type} not implemented')