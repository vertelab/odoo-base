# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import requests
import logging
import base64

_logger = logging.getLogger(__name__)


class WebsiteAnalyticsProvider(models.Model):
    _inherit = 'website.analytics.provider'

    @api.model
    def _get_provider_types(self):
        types = super()._get_provider_types()
        types.append(('matomo', 'Matomo'))
        return types

    def _fetch_matomo_report_image(self, resource, report_type):
        self.ensure_one()

        if not self.base_url or not self.token_auth:
            raise UserError(_('Matomo provider is not properly configured.'))

        if not resource.analytics_site_id:
            raise UserError(_('Site ID is required for Matomo analytics.'))

        base_url = self.base_url.rstrip('/')

        # Build ImageGraph URL
        params = {
            'module': 'API',
            'method': 'ImageGraph.get',
            'idSite': resource.analytics_site_id,
            'apiModule': report_type.api_module,
            'apiAction': report_type.api_action,
            'period': report_type.period,
            'date': report_type.date,
            'width': report_type.width,
            'height': report_type.height,
            'graphType': report_type.graph_type,
        }

        data = {
            'token_auth': self.token_auth,
        }

        try:
            response = requests.post(f"{base_url}/index.php", params=params, data=data, timeout=30)
            response.raise_for_status()

            # Check if response is actually an image
            content_type = response.headers.get('Content-Type', '')
            if 'image' in content_type or response.content[:8] == b'\x89PNG\r\n\x1a\n':
                # Encode image to base64
                image_base64 = base64.b64encode(response.content).decode('utf-8')
                return image_base64
            else:
                # Might be an error message
                _logger.error(f"Matomo returned non-image content for {report.name}: {response.text[:200]}")
                return None

        except requests.exceptions.RequestException as e:
            _logger.error(f"Failed to fetch Matomo report image for {report.name}: {e}")
            return None

    def _fetch_matomo_analytics(self, resource):
        self.ensure_one()

        if not self.base_url or not self.token_auth:
            raise UserError(_('Matomo provider is not properly configured.'))

        if not resource.analytics_site_id:
            raise UserError(_('Site ID is required for Matomo analytics.'))

        # Fetch overall site metrics
        self._fetch_matomo_site_summary(resource)

        # Fetch per-page metrics if pages are configured
        if resource.analytics_page_ids:
            self._fetch_matomo_page_metrics(resource)

        # Fetch traffic sources
        self._fetch_matomo_traffic_sources(resource)

    def _fetch_matomo_site_summary(self, resource):
        self.ensure_one()

        base_url = self.base_url.rstrip('/')

        params = {
            'module': 'API',
            'method': 'VisitsSummary.get',
            'idSite': resource.analytics_site_id,
            'period': 'day',
            'date': 'today',
            'format': 'json',
        }

        data = {
            'token_auth': self.token_auth,
        }

        try:
            response = requests.post(f"{base_url}/index.php", params=params, data=data, timeout=30)
            response.raise_for_status()
            result = response.json()

            # Create or update result for today
            self._create_or_update_result(resource, result)

        except requests.exceptions.RequestException as e:
            _logger.error(f"Failed to fetch Matomo site summary: {e}")
            raise UserError(_('Failed to connect to Matomo: %s') % str(e))

    def _fetch_matomo_page_metrics(self, resource):
        self.ensure_one()

        base_url = self.base_url.rstrip('/')

        params = {
            'module': 'API',
            'method': 'Actions.getPageUrls',
            'idSite': resource.analytics_site_id,
            'period': 'day',
            'date': 'today',
            'format': 'json',
        }

        data = {
            'token_auth': self.token_auth,
        }

        try:
            response = requests.post(f"{base_url}/index.php", params=params, data=data, timeout=30)
            response.raise_for_status()
            result = response.json()

            # Match pages and create results
            for page in resource.analytics_page_ids:
                page_data = self._find_page_in_matomo_data(page, result)
                if page_data:
                    self._create_or_update_result(resource, page_data, page_id=page.id)

        except requests.exceptions.RequestException as e:
            _logger.error(f"Failed to fetch Matomo page metrics: {e}")
            raise UserError(_('Failed to fetch page metrics: %s') % str(e))

    def _fetch_matomo_traffic_sources(self, resource):
        self.ensure_one()

        base_url = self.base_url.rstrip('/')

        params = {
            'module': 'API',
            'method': 'Referrers.getAll',
            'idSite': resource.analytics_site_id,
            'period': 'day',
            'date': 'today',
            'format': 'json',
        }

        data = {
            'token_auth': self.token_auth,
        }

        try:
            response = requests.post(f"{base_url}/index.php", params=params, data=data, timeout=30)
            response.raise_for_status()
            result = response.json()

            traffic_data = self._parse_traffic_sources(result)

            # Update today's result with traffic data
            result_record = self.env['website.analytics.result'].search([
                ('resource_model', '=', resource._name),
                ('resource_id', '=', resource.id),
                ('date', '=', fields.Date.today()),
                ('page_id', '=', False),
            ], limit=1)

            if result_record:
                result_record.write(traffic_data)

        except requests.exceptions.RequestException as e:
            _logger.error(f"Failed to fetch Matomo traffic sources: {e}")

    def _find_page_in_matomo_data(self, page, matomo_data):
        """Find matching page data in Matomo response"""
        if not isinstance(matomo_data, list):
            return None

        for item in matomo_data:
            if item.get('label') == page.url or item.get('url') == page.url:
                return item

        return None

    def _parse_traffic_sources(self, data):
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

    def _create_or_update_result(self, resource, data, page_id=None):
        self.ensure_one()

        values = {
            'resource_model': resource._name,
            'resource_id': resource.id,
            'page_id': page_id,
            'date': fields.Date.today(),
            'page_views': data.get('nb_pageviews', 0),
            'unique_visitors': data.get('nb_uniq_visitors', 0),
            'bounce_rate': float(str(data.get('bounce_rate', '0')).replace('%', '').replace('\u00a0', '').strip()),
            'avg_time_on_page': data.get('avg_time_on_page', data.get('avg_time_on_site', 0.0)),
        }

        # Check if result already exists
        domain = [
            ('resource_model', '=', resource._name),
            ('resource_id', '=', resource.id),
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