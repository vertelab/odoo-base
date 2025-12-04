# -*- coding: utf-8 -*-
import logging
from serpapi import GoogleSearch

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class SerpProvider(models.Model):
    _inherit = 'serp.provider'

    provider_type = fields.Selection(
        selection_add=[
            ('serpapi', 'SerpAPI'),
        ],
        ondelete={'serpapi': 'cascade'}
    )

    def _search_serpapi(self, keyword, domain=None, country='SE', language='sv'):
        """SerpAPI implementation"""
        self.ensure_one()

        _logger.info(f"Searching for '{keyword}' with SerpAPI (domain: {domain}, country: {country})")

        # Check if API key is configured
        if not self.api_key:
            raise UserError(_('SerpAPI requires an API key. Please configure it in the provider settings.'))

        # Prepare search parameters
        params = {
            "q": keyword,
            "gl": country,  # Country code (uppercase like 'SE')
            "hl": language,  # Language
            "num": self._get_max_position(),  # Number of results
            "api_key": self.api_key,
        }

        # Add search engine if specified
        if self.search_engine:
            params["engine"] = self.search_engine

        try:
            # Execute search via SerpAPI
            search = GoogleSearch(params)
            results = search.get_dict()

            # Parse results
            matches = self._parse_serp_serpapi(results, keyword, domain)

            return matches if matches else [{
                'success': False,
                'keyword': keyword,
                'domain': domain,
                'position': None,
                'url': None,
                'error': f'Domain {domain} not found in search results'
            }]

        except Exception as e:
            _logger.error(f"SerpAPI search failed for '{keyword}': {str(e)}")
            return [{
                'success': False,
                'keyword': keyword,
                'domain': domain,
                'position': None,
                'url': None,
                'error': str(e)
            }]

    def _parse_serp_serpapi(self, results, keyword, domain=None):
        """Parse SerpAPI results and find domain position"""
        self.ensure_one()

        # Check if we got organic results
        organic_results = results.get('organic_results', [])

        if not organic_results:
            _logger.warning(f"No organic results found for keyword '{keyword}'")
            return []

        matches = []

        for idx, result in enumerate(organic_results, start=1):
            link = result.get('link', '')

            if not link:
                continue

            # Use the base model's normalize method
            result_domain = self._normalize_domain(link)

            if not result_domain:
                continue

            # Check if this result matches our target domain
            if domain and result_domain and domain.lower() == result_domain.lower():
                _logger.info(f"Found '{result_domain}' at position {idx} for keyword '{keyword}'")

                matches.append({
                    'success': True,
                    'keyword': keyword,
                    'domain': result_domain,
                    'position': idx,
                    'url': link,
                    'title': result.get('title'),
                    'snippet': result.get('snippet'),
                    'error': None
                })

        if not matches and domain:
            _logger.info(f"Domain '{domain}' not found in top {len(organic_results)} results for '{keyword}'")

        return matches