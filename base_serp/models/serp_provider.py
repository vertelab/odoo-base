# -*- coding: utf-8 -*-
import logging
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import time
import random

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class SerpProvider(models.Model):
    _name = 'serp.provider'
    _description = 'SERP Provider'
    _order = 'sequence, name'

    name = fields.Char(string='Provider Name', required=True)
    provider_type = fields.Selection(
        selection=[
            ('beautifulsoup', 'BeautifulSoup (Web Scraping)'),
        ],
        string='Provider Type',
        required=True,
        default='beautifulsoup'
    )
    sequence = fields.Integer(string='Sequence', default=10)
    active = fields.Boolean(string='Active', default=True)

    # Configuration fields
    rate_limit_delay = fields.Float(
        string='Rate Limit Delay (seconds)',
        default=2.0,
        help='Delay between requests to avoid being blocked'
    )
    timeout = fields.Integer(
        string='Request Timeout (seconds)',
        default=10,
        help='Maximum time to wait for a response'
    )
    num_results = fields.Integer(
        string='Number of Results',
        default=10,
        help='Number of results to fetch per page'
    )
    search_engine = fields.Selection(
        selection=[
            ('google', 'Google'),
            # Future: ('bing', 'Bing'), ('duckduckgo', 'DuckDuckGo')
        ],
        string='Search Engine',
        default='google',
        required=True,
        help='Search engine to use for queries'
    )

    # API credentials (for future providers)
    api_key = fields.Char(string='API Key', help='API key for provider (if required)')
    api_secret = fields.Char(string='API Secret', help='API secret for provider (if required)')

    # Statistics
    total_searches = fields.Integer(string='Total Searches', readonly=True, default=0)
    last_search_date = fields.Datetime(string='Last Search Date', readonly=True)

    _sql_constraints = [
        ('unique_provider_type_engine', 'unique(provider_type, search_engine)',
         'Provider type and search engine combination must be unique!')
    ]

    def _normalize_domain(self, url):
        """
        Normalize a URL or domain for comparison

        Examples:
            'https://www.odoo.com/page' -> 'odoo.com'
            'http://Odoo.COM' -> 'odoo.com'
            'www.odoo.com' -> 'odoo.com'
            'ODOO.COM' -> 'odoo.com'

        Returns:
            str: Normalized domain (lowercase, no www., no protocol, no path)
        """
        if not url:
            return None

        # Convert to string and lowercase
        domain = str(url).lower().strip()

        # Remove protocol
        domain = domain.replace('https://', '').replace('http://', '')

        # Remove www.
        domain = domain.replace('www.', '')

        # Remove path (take only domain part before first /)
        domain = domain.split('/')[0]

        # Remove trailing dots
        domain = domain.rstrip('.')

        return domain

    def execute_search(self, keyword, domain=None, country='SE', language='sv'):
        """Execute search based on provider_type"""
        self.ensure_one()

        if not self.provider_type:
            raise UserError(_('Provider type is not set'))

        method_name = f'_search_{self.provider_type}'
        method = getattr(self, method_name, None)

        if not method:
            raise NotImplementedError(
                _('Provider method %s not implemented') % method_name
            )

        try:
            # Normalize domain if provided, otherwise None
            normalized_domain = self._normalize_domain(domain) if domain else None

            # Execute the search
            result = method(keyword, normalized_domain, country, language)

            # Update statistics
            self.sudo().write({
                'total_searches': self.total_searches + 1,
                'last_search_date': fields.Datetime.now()
            })

            return result

        except Exception as e:
            _logger.error(
                f"Error executing search with provider {self.name}: {str(e)}"
            )
            raise UserError(
                _('Search failed: %s') % str(e)
            )

    def _search_beautifulsoup(self, keyword, domain=None, country='SE', language='sv'):
        """BeautifulSoup web scraping implementation"""
        self.ensure_one()

        _logger.info(f"Searching for '{keyword}' with BeautifulSoup (domain: {domain})")

        # Get search results HTML
        html = self._get_google_results(keyword, country, language)

        if not html:
            return {
                'success': False,
                'keyword': keyword,
                'domain': domain,
                'position': None,
                'url': None,
                'error': 'Failed to fetch search results'
            }

        # Parse the results
        result = self._parse_serp_beautifulsoup(html, keyword, domain)

        # Add delay to respect rate limiting
        time.sleep(self.rate_limit_delay)

        return result

    def _get_google_results(self, keyword, country, language):
        """Fetch Google search results HTML"""
        self.ensure_one()

        google_url = "https://www.google.com/search"
        ua = UserAgent()

        # Generate random user agent
        headers = {
            "User-Agent": ua.random,
            "Accept-Language": f"{language}-{country},{language};q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
        }

        params = {
            "q": keyword,
            "gl": country,  # Country
            "hl": language,  # Language
            "num": self.num_results,  # Number of results
        }

        try:
            response = requests.get(
                google_url,
                headers=headers,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.text

        except requests.exceptions.RequestException as e:
            _logger.error(f"Error fetching Google results for '{keyword}': {str(e)}")
            return None

    def _parse_serp_beautifulsoup(self, html, keyword, domain=None):
        """Parse Google SERP HTML and find domain position"""
        self.ensure_one()

        soup = BeautifulSoup(html, "html.parser")

        # Google search result containers
        results = soup.find_all("div", class_="g")

        if not results:
            # Try alternative container class (Google changes this sometimes)
            results = soup.find_all("div", class_="tF2Cxc")

        matches = []

        for idx, result in enumerate(results, start=1):
            # Find the link
            link_tag = result.find("a")

            if not link_tag or not link_tag.get("href"):
                continue

            url = link_tag["href"]

            # Extract domain from URL
            try:
                result_domain = url.replace('https://', '').replace('http://', '')
                result_domain = result_domain.split('/')[0]
                result_domain = result_domain.replace('www.', '')
            except:
                result_domain = url

            # If domain filter is provided, only save matching results
            # If no domain filter, save ALL results
            if not domain or domain.lower() in result_domain.lower():
                _logger.info(f"Found '{result_domain}' at position {idx} for keyword '{keyword}'")

                # Extract title
                title_tag = result.find("h3")
                title = title_tag.get_text() if title_tag else None

                # Extract snippet
                snippet_tag = result.find("div", class_="VwiC3b")
                if not snippet_tag:
                    snippet_tag = result.find("span", class_="aCOpRe")
                snippet = snippet_tag.get_text() if snippet_tag else None

                matches.append({
                    'success': True,
                    'keyword': keyword,
                    'domain': result_domain,
                    'position': idx,
                    'url': url,
                    'title': title,
                    'snippet': snippet,
                    'error': None
                })

        if not matches and domain:
            _logger.info(f"Domain '{domain}' not found in top {len(results)} results for '{keyword}'")

        return matches

    def test_search(self):
        """Test the provider with a sample search"""
        self.ensure_one()

        # Test search
        test_keyword = "odoo erp"
        test_domain = "odoo.com"

        try:
            result = self.execute_search(
                keyword=test_keyword,
                domain=test_domain,
                country='SE',
                language='sv'
            )

            if result.get('success'):
                if result.get('position'):
                    message = _(
                        'Test successful!\n\n'
                        'Domain: %s\n'
                        'Keyword: %s\n'
                        'Position: %s\n'
                        'URL: %s'
                    ) % (
                                  test_domain,
                                  test_keyword,
                                  result['position'],
                                  result['url']
                              )
                else:
                    message = _(
                        'Test successful, but domain not found in top results.\n\n'
                        'Domain: %s\n'
                        'Keyword: %s'
                    ) % (test_domain, test_keyword)
            else:
                message = _('Test failed: %s') % result.get('error', 'Unknown error')

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Provider Test'),
                    'message': message,
                    'type': 'success' if result.get('success') else 'danger',
                    'sticky': True,
                }
            }

        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Provider Test Failed'),
                    'message': str(e),
                    'type': 'danger',
                    'sticky': True,
                }
            }