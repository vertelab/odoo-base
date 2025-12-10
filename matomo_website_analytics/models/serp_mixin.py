# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import requests
import logging
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)


class SERPMixin(models.AbstractModel):
    _inherit = 'serp.mixin'

    @api.onchange('analytics_provider_id')
    def _analytics_provider_id(self):
        if self.analytics_provider_id == self.env.ref('matomo_website_analytics.analytics_provider_matomo'):
            template = self.env.ref('matomo_website_analytics.matomo_analytics_template', raise_if_not_found=False)
            if template:
                self.analytics_report_template_id = template.id
        return None

    def _get_analytics_report(self, report_type_uuid):
        self.ensure_one()
        if not report_type_uuid:
            _logger.warning("No report_type_uuid provided to _get_analytics_report.")
            return None

        report_type = self.env['website.analytics.report.type'].search([
            ('report_type_id', '=', report_type_uuid)
        ], limit=1)

        if not report_type:
            _logger.warning(f"Analytics report type not found for UUID: {report_type_uuid}")
            return None

        if not self.analytics_provider_id:
            _logger.warning(f"No analytics provider configured for {self.display_name}. Cannot fetch report {report_type.name}.")
            return None

        try:
            image_data = self.analytics_provider_id.fetch_report_image(self, report_type)
            return image_data
        except Exception as e:
            _logger.error(
                f"Failed to fetch analytics report '{report_type.name}' for {self.display_name}: {str(e)}",
                exc_info=True
            )
            return None

    def action_fetch_analytics(self):
        self.ensure_one()

        if not self.analytics_provider_id:
            raise UserError(_('Please configure an analytics provider first.'))

        if self.analytics_provider_id.provider_type != 'matomo':
            return super().action_fetch_analytics()

        return self._fetch_matomo_analytics()

    def _fetch_matomo_analytics(self):
        self.ensure_one()

        provider = self.analytics_provider_id

        if not provider.base_url or not provider.token_auth:
            raise UserError(_('Matomo provider is not properly configured.'))

        if not self.analytics_site_id:
            raise UserError(_('Site ID is required for Matomo analytics.'))

        # Fetch overall site metrics
        self._fetch_matomo_site_summary()

        # Fetch per-page metrics if pages are configured
        if self.analytics_page_ids:
            self._fetch_matomo_page_metrics()

        # Fetch traffic sources
        self._fetch_matomo_traffic_sources()

        # Update last sync time
        self.analytics_last_sync = fields.Datetime.now()

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Analytics data fetched successfully.'),
                'type': 'success',
                'sticky': False,
            }
        }

    def _fetch_matomo_site_summary(self):
        self.ensure_one()

        provider = self.analytics_provider_id
        base_url = provider.base_url.rstrip('/')

        params = {
            'module': 'API',
            'method': 'VisitsSummary.get',
            'idSite': self.analytics_site_id,
            'period': 'day',
            'date': 'today',
            'format': 'json',
        }

        data = {
            'token_auth': provider.token_auth,
        }

        try:
            response = requests.post(f"{base_url}/index.php", params=params, data=data, timeout=30)
            response.raise_for_status()
            result = response.json()

            # Create or update result for today
            self._create_or_update_result(result)

        except requests.exceptions.RequestException as e:
            _logger.error(f"Failed to fetch Matomo site summary: {e}")
            raise UserError(_('Failed to connect to Matomo: %s') % str(e))

    def _fetch_matomo_page_metrics(self):
        self.ensure_one()

        provider = self.analytics_provider_id
        base_url = provider.base_url.rstrip('/')

        params = {
            'module': 'API',
            'method': 'Actions.getPageUrls',
            'idSite': self.analytics_site_id,
            'period': 'day',
            'date': 'today',
            'format': 'json',
        }

        data = {
            'token_auth': provider.token_auth,
        }

        try:
            response = requests.post(f"{base_url}/index.php", params=params, data=data, timeout=30)
            response.raise_for_status()
            result = response.json()

            # Match pages and create results
            for page in self.analytics_page_ids:
                page_data = self._find_page_in_matomo_data(page, result)
                if page_data:
                    self._create_or_update_result(page_data, page_id=page.id)

        except requests.exceptions.RequestException as e:
            _logger.error(f"Failed to fetch Matomo page metrics: {e}")
            raise UserError(_('Failed to fetch page metrics: %s') % str(e))

    def _fetch_matomo_traffic_sources(self):
        self.ensure_one()

        provider = self.analytics_provider_id
        base_url = provider.base_url.rstrip('/')

        params = {
            'module': 'API',
            'method': 'Referrers.getAll',
            'idSite': self.analytics_site_id,
            'period': 'day',
            'date': 'today',
            'format': 'json',
        }

        data = {
            'token_auth': provider.token_auth,
        }

        try:
            response = requests.post(f"{base_url}/index.php", params=params, data=data, timeout=30)
            response.raise_for_status()
            result = response.json()

            traffic_data = self._parse_traffic_sources(result)

            # Update today's result with traffic data
            result_record = self.env['website.analytics.result'].search([
                ('resource_model', '=', self._name),
                ('resource_id', '=', self.id),
                ('date', '=', fields.Date.today()),
                ('page_id', '=', False),
            ], limit=1)

            if result_record:
                result_record.write(traffic_data)

        except requests.exceptions.RequestException as e:
            _logger.error(f"Failed to fetch Matomo traffic sources: {e}")

    def _find_page_in_matomo_data(self, page, matomo_data):
        if not isinstance(matomo_data, list):
            return None

        for item in matomo_data:
            if item.get('label') == page.url or item.get('url') == page.url:
                return item

        return None

    def _parse_traffic_sources(self, data):
        """Parse traffic source data from Matomo"""
        traffic_data = {
            'traffic_search': 0,
            'traffic_direct': 0,
            'traffic_referral': 0,
            'traffic_social': 0,
        }

        if not isinstance(data, list):
            return traffic_data

        for item in data:
            label = item.get('label', '').lower()
            visits = item.get('nb_visits', 0)

            if 'search' in label or 'google' in label or 'bing' in label:
                traffic_data['traffic_search'] += visits
            elif 'direct' in label:
                traffic_data['traffic_direct'] += visits
            elif 'social' in label or 'facebook' in label or 'twitter' in label:
                traffic_data['traffic_social'] += visits
            else:
                traffic_data['traffic_referral'] += visits

        return traffic_data

    def _create_or_update_result(self, data, page_id=None):
        self.ensure_one()

        values = {
            'resource_model': self._name,
            'resource_id': self.id,
            'page_id': page_id,
            'date': fields.Date.today(),
            'page_views': data.get('nb_pageviews', 0),
            'unique_visitors': data.get('nb_uniq_visitors', 0),
            'bounce_rate': float(str(data.get('bounce_rate', '0')).replace('%', '').replace('\u00a0', '').strip()),
            'avg_time_on_page': data.get('avg_time_on_page', data.get('avg_time_on_site', 0.0)),
        }

        # Check if result already exists
        domain = [
            ('resource_model', '=', self._name),
            ('resource_id', '=', self.id),
            ('date', '=', fields.Date.today()),
        ]

        if page_id:
            domain.append(('page_id', '=', page_id))
        else:
            domain.append(('page_id', '=', False))

        result = self.env['website.analytics.result'].search(domain, limit=1)

        if result:
            result.write(values)
        else:
            self.env['website.analytics.result'].create(values)