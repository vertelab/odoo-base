# -*- coding: utf-8 -*-
import logging
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import time

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class SerpProvider(models.Model):
    _name = 'serp.provider'
    _description = 'SERP Provider'
    _order = 'name'

    name = fields.Char(string='Provider Name', required=True)
    provider_type = fields.Selection(
        selection=[
            ('beautifulsoup', 'BeautifulSoup (Web Scraping)'),
        ],
        string='Provider Type',
        required=True,
        default='beautifulsoup'
    )
    active = fields.Boolean(string='Active', default=True)

    search_engine = fields.Selection(
        selection=[
            ('google', 'Google'),
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

        domain = str(url).lower().strip()
        domain = domain.replace('https://', '').replace('http://', '')
        domain = domain.replace('www.', '')
        domain = domain.split('/')[0]
        domain = domain.rstrip('.')

        return domain

    def _get_max_position(self):
        """Get maximum position from system parameters"""
        return int(self.env['ir.config_parameter'].sudo().get_param('base_serp.max_position', 50))

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
            normalized_domain = self._normalize_domain(domain) if domain else None
            result = method(keyword, normalized_domain, country, language)

            # Update statistics
            self.sudo().write({
                'total_searches': self.total_searches + 1,
                'last_search_date': fields.Datetime.now()
            })

            return result

        except Exception as e:
            _logger.error(f"Error executing search with provider {self.name}: {str(e)}")
            raise UserError(_('Search failed: %s') % str(e))

    def _search_beautifulsoup(self, keyword, domain=None, country='SE', language='sv'):
        """BeautifulSoup web scraping implementation"""
        self.ensure_one()

        _logger.info(f"Searching for '{keyword}' with BeautifulSoup (domain: {domain}, country: {country})")

        html = self._get_google_results(keyword, country, language)

        if not html:
            return [{
                'success': False,
                'keyword': keyword,
                'domain': domain,
                'position': None,
                'url': None,
                'error': 'Failed to fetch search results'
            }]

        # Parse the results
        matches = self._parse_serp_beautifulsoup(html, keyword, domain)

        return matches if matches else [{
            'success': False,
            'keyword': keyword,
            'domain': domain,
            'position': None,
            'url': None,
            'error': f'Domain {domain} not found in search results'
        }]

    def _get_google_results(self, keyword, country, language):
        """Fetch Google search results HTML"""
        self.ensure_one()

        google_url = "https://www.google.com/search"
        ua = UserAgent()

        headers = {
            "User-Agent": ua.random,
            "Accept-Language": f"{language}-{country},{language};q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
        }

        params = {
            "q": keyword,
            "gl": country,
            "hl": language,
            "num": self._get_max_position(),
        }

        try:
            response = requests.get(
                google_url,
                headers=headers,
                params=params,
                timeout=10  # Hardcoded timeout
            )
            response.raise_for_status()
            return response.text

        except requests.exceptions.RequestException as e:
            _logger.error(f"Error fetching Google results for '{keyword}': {str(e)}")
            return None

    def _parse_serp_beautifulsoup(self, html, keyword, domain):
        """Parse Google SERP HTML and find domain position"""
        self.ensure_one()

        soup = BeautifulSoup(html, "html.parser")
        results = soup.find_all("div", class_="g")

        if not results:
            results = soup.find_all("div", class_="tF2Cxc")

        matches = []

        for idx, result in enumerate(results, start=1):
            link_tag = result.find("a")

            if not link_tag or not link_tag.get("href"):
                continue

            url = link_tag["href"]

            try:
                result_domain = self._normalize_domain(url)
            except:
                continue

            # Check if this result matches our target domain
            if domain and result_domain and domain.lower() == result_domain.lower():
                _logger.info(f"Found '{result_domain}' at position {idx} for keyword '{keyword}'")

                title_tag = result.find("h3")
                title = title_tag.get_text() if title_tag else None

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

        test_keyword = "odoo erp"
        test_domain = "odoo.com"

        try:
            results = self.execute_search(
                keyword=test_keyword,
                domain=test_domain,
                country='SE',
                language='sv'
            )

            # Get first result
            result = results[0] if results else {}

            if result.get('success') and result.get('position'):
                message = _(
                    'Test successful!\n\n'
                    'Domain: %s\n'
                    'Keyword: %s\n'
                    'Position: %s\n'
                    'URL: %s'
                ) % (test_domain, test_keyword, result['position'], result['url'])
                msg_type = 'success'
            else:
                message = _(
                    'Test completed, but domain not found in top results.\n\n'
                    'Domain: %s\n'
                    'Keyword: %s'
                ) % (test_domain, test_keyword)
                msg_type = 'warning'

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Provider Test'),
                    'message': message,
                    'type': msg_type,
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