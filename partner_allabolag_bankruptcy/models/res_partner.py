import re
import logging
import time
from allabolag import Company
from markupsafe import Markup
from odoo import models, api, _

_logger = logging.getLogger(__name__)


class Partner(models.Model):
    _inherit = 'res.partner'

    def _extract_org_number_from_url(self, url):
        """Extract organization number from company URL"""
        # URL format: /foretag/company-name/location/-/5592742299
        match = re.search(r'/-/(\d+)$', url)
        result = match.group(1) if match else None
        _logger.info(f"_extract_org_number_from_url: input='{url}' -> output='{result}'")
        return result

    def _get_partners_with_allabolag(self):
        return self.search([
            '|',
            ('linkTo', 'ilike', 'allabolag.se'),
            ('company_registry', '!=', False)
        ])

    def _parse_org_number(self, value):
        if not value:
            return None

        # If it's an Allabolag URL, extract from URL
        if 'allabolag' in value.lower():
            return self._extract_org_number_from_url(value)

        # Otherwise, clean it (remove spaces, dashes, etc)
        cleaned = re.sub(r'\D', '', value)
        return cleaned if cleaned else None

    def _get_org_number_from_partner(self, partner):
        # Try linkTo first
        org_number = self._parse_org_number(partner.linkTo)
        if org_number:
            _logger.info(f"Using org_number from linkTo: {org_number}")
            return org_number

        # Fallback to company_registry
        org_number = self._parse_org_number(partner.company_registry)
        if org_number:
            _logger.info(f"Using org_number from company_registry: {org_number}")
            return org_number

        _logger.warning(f"No org number found for partner: {partner.name}")
        return None

    def _get_company_details(self, org_number):
        _logger.info(f"Calling Company() with org_number: '{org_number}' (type: {type(org_number)})")

        try:
            company = Company(org_number)
            return company.data
        except Exception as e:
            _logger.error(f"Failed to fetch details for {org_number}: {e}")
            return None

    def _check_bankruptcy_status(self, company_data):
        if not company_data:
            return None

        company_info = company_data.get('company', {})
        status_remarks = company_info.get('statusRemarks', [])

        # Look for bankruptcy in status remarks
        for remark in status_remarks:
            desc = remark.get('desc', '').lower()
            if 'konkurs' in desc:
                return {
                    'bankruptcy_date': remark.get('date', False),
                    'bankruptcy_status': remark.get('desc', False),
                    'is_ended': 'avslutad' in desc or 'ended' in desc
                }
        return None

    def _extract_company_info(self, company_data):
        if not company_data:
            return {
                'name': 'Unknown',
                'county': False,
                'municipality': False,
                'industry': False,
                'org_number': False
            }

        company_info = company_data.get('company', {})

        # Extract location
        location = company_info.get('location', {})
        county = location.get('county', False)
        municipality = location.get('municipality', False)

        # Extract industries
        industries = company_info.get('industries', [])
        industry_names = [ind.get('name', '') for ind in industries[:2]]
        industry_text = ', '.join(industry_names) if industry_names else False

        return {
            'name': company_info.get('name', 'Unknown'),
            'county': county,
            'municipality': municipality,
            'industry': industry_text,
            'org_number': company_info.get('orgnr', False)
        }

    def _format_chatter_message(self, partner, company_info, bankruptcy_info):
        status_text = "ended" if bankruptcy_info['is_ended'] else "commenced"

        message_body = f"""
            <p><strong>⚠️ Bankruptcy Alert</strong></p>
            <ul>
                <li><strong>Status:</strong> Bankruptcy {status_text}</li>
                <li><strong>Bankruptcy Status:</strong> {bankruptcy_info['bankruptcy_status']}</li>
                <li><strong>Date:</strong> {bankruptcy_info['bankruptcy_date'] or 'N/A'}</li>
                <li><strong>Source:</strong> <a href="{partner.linkTo or f"https://allabolag.se/foretag/-/-/-/{company_info['org_number']}"}" target="_blank">View on Allabolag</a></li>
            </ul>
        """

        partner.message_post(
            body=Markup(message_body),
            subject=f"Bankruptcy {status_text.title()}: {company_info['name']}",
            message_type='notification',
            subtype_xmlid='mail.mt_note'
        )

        _logger.info(f"Posted bankruptcy notification for {partner.name} (org: {company_info['org_number']})")

    def cron_process_bankrupt_companies(self):
        """
        Check all partners with Allabolag data for bankruptcy status.
        No web scraping needed - uses allabolag library directly!
        """
        # Get all partners with Allabolag data
        partners = self._get_partners_with_allabolag()

        if not partners:
            return

        _logger.info(f"Checking {len(partners)} partners for bankruptcy status...")

        bankrupt_found = 0
        checked = 0
        errors = 0

        for partner in partners:
            try:
                # Get organization number
                org_number = self._get_org_number_from_partner(partner)

                if not org_number:
                    _logger.warning(f"Could not extract org number for partner: {partner.name}")
                    continue

                _logger.info(f"About to call _get_company_details with: '{org_number}'")

                # Fetch company details from allabolag
                company_data = self._get_company_details(org_number)

                if not company_data:
                    errors += 1
                    continue

                checked += 1

                # Check bankruptcy status
                bankruptcy_info = self._check_bankruptcy_status(company_data)

                if bankruptcy_info:
                    # Company is bankrupt! Extract info and notify
                    company_info = self._extract_company_info(company_data)

                    self._format_chatter_message(
                        partner,
                        company_info,
                        bankruptcy_info
                    )

                    bankrupt_found += 1
                    _logger.info(f"Bankruptcy found: {company_info['name']} ({org_number})")

                # Rate limiting - be nice to the API
                time.sleep(0.5)

            except Exception as e:
                errors += 1
                _logger.error(f"Failed to process partner {partner.name}: {e}")

        _logger.info(
            f"Bankruptcy check complete. Checked: {checked}, Bankruptcies found: {bankrupt_found}, Errors: {errors}")