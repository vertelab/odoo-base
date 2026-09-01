# -*- coding: utf-8 -*-
import logging
import re

from odoo import _, fields, models

_logger = logging.getLogger(__name__)


class ForetagsapiMappingMixin(models.AbstractModel):
    """Helper mixin that maps FöretagsAPI.se responses to Odoo values."""

    _name = 'foretagsapi.mapping.mixin'
    _description = 'FöretagsAPI Response Mapping'

    def _foretagsapi_format_org_number(self, org_number):
        """Return an organisation number formatted as NNNNNN-NNNN."""
        if not org_number:
            return False
        digits = re.sub(r'\D', '', str(org_number))
        if len(digits) != 10:
            return digits or False
        return f'{digits[:6]}-{digits[6:]}'

    def _foretagsapi_org_number_to_vat(self, org_number):
        """Build a Swedish VAT number from an organisation number."""
        if not org_number:
            return False
        digits = re.sub(r'\D', '', str(org_number))
        if len(digits) != 10:
            return False
        return f'SE{digits}01'

    def _foretagsapi_parse_date(self, value):
        if not value:
            return False
        try:
            return fields.Date.to_date(value)
        except Exception:
            return False

    def _foretagsapi_parse_float(self, value, allow_negative=False):
        if value is None:
            return False
        try:
            number = float(value)
            if not allow_negative and number < 0:
                return False
            return number
        except (ValueError, TypeError):
            return False

    def _foretagsapi_country_sweden(self):
        return self.env.ref('base.se', raise_if_not_found=False)

    def _foretagsapi_map_address(self, company):
        address = company.get('postalAddress') or {}
        vals = {
            'street': address.get('street') or False,
            'zip': address.get('postalCode') or False,
            'city': address.get('city') or False,
        }
        country = self._foretagsapi_country_sweden()
        if country:
            vals['country_id'] = country.id
        return vals

    def _foretagsapi_map_sni(self, company):
        """Return a list of res.sni records from the SNI codes in the response."""
        sni_codes = company.get('sniCodes') or {}
        sni_env = self.env['res.sni']
        records = self.env['res.sni']

        for index in range(1, 6):
            code = sni_codes.get(f'sni{index}')
            name = sni_codes.get(f'sni{index}_name')
            if not code:
                continue
            # Skip unknown placeholder
            if code == '00000':
                continue
            existing = sni_env.search([('code', '=', code)], limit=1)
            if existing:
                records |= existing
                continue
            # Some descriptions are generic; prefer the API description if present
            description = name or ''
            create_vals = {
                'name': description or code,
                'code': code,
                'description': description,
            }
            try:
                new_sni = sni_env.create(create_vals)
                records |= new_sni
            except Exception as e:
                _logger.warning('Could not create SNI %s: %s', code, e)

        return records

    def _foretagsapi_map_financials(self, company):
        """Return a list of create-values for res.partner.financials."""
        financials = company.get('financials')
        if not financials:
            return []

        vals = {
            'fiscal_year': str(financials.get('year')) if financials.get('year') else False,
            'net_sales': self._foretagsapi_parse_float(financials.get('revenue'), allow_negative=True),
            'operating_profit': self._foretagsapi_parse_float(financials.get('operatingResult'), allow_negative=True),
            'net_result': self._foretagsapi_parse_float(financials.get('netResult'), allow_negative=True),
            'result_after_financial_items': self._foretagsapi_parse_float(financials.get('resultAfterFinancialItems'), allow_negative=True),
            'profit_before_tax': self._foretagsapi_parse_float(financials.get('profitBeforeTax'), allow_negative=True),
            'total_assets': self._foretagsapi_parse_float(financials.get('totalAssets'), allow_negative=True),
            'equity': self._foretagsapi_parse_float(financials.get('equity'), allow_negative=True),
            'current_assets': self._foretagsapi_parse_float(financials.get('currentAssets'), allow_negative=True),
            'current_liabilities': self._foretagsapi_parse_float(financials.get('currentLiabilities'), allow_negative=True),
            'cash_and_bank': self._foretagsapi_parse_float(financials.get('cashAndBank'), allow_negative=True),
            'long_term_liabilities': self._foretagsapi_parse_float(financials.get('longTermLiabilities'), allow_negative=True),
            'fixed_assets': self._foretagsapi_parse_float(financials.get('fixedAssets'), allow_negative=True),
            'restricted_equity': self._foretagsapi_parse_float(financials.get('restrictedEquity'), allow_negative=True),
            'unrestricted_equity': self._foretagsapi_parse_float(financials.get('unrestrictedEquity'), allow_negative=True),
            'untaxed_reserves': self._foretagsapi_parse_float(financials.get('untaxedReserves'), allow_negative=True),
            'proposed_dividend': self._foretagsapi_parse_float(financials.get('proposedDividend'), allow_negative=True),
            'employees': self._foretagsapi_parse_float(financials.get('employees'), allow_negative=False),
            'solidity': self._foretagsapi_parse_float(financials.get('solidity'), allow_negative=True),
            'operating_margin': self._foretagsapi_parse_float(financials.get('operatingMargin'), allow_negative=True),
            'fiscal_year_start': self._foretagsapi_parse_date(financials.get('fiscalYearStart')),
            'fiscal_year_end': self._foretagsapi_parse_date(financials.get('fiscalYearEnd')),
            'taxonomy': financials.get('taxonomy') or False,
            'currency': financials.get('currency') or False,
        }
        # Drop empty values to keep the record clean
        return [(0, 0, {k: v for k, v in vals.items() if v not in (False, None, '')})]

    def _foretagsapi_map_estimates(self, company):
        """Map revenue/employee estimate envelopes to Odoo values."""
        revenue = company.get('revenue_estimate') or {}
        employees = company.get('employees_estimate') or {}

        def extract_value(envelope):
            if not envelope or envelope.get('type') == 'none':
                return False, False
            value = envelope.get('value')
            if value is None or value == '':
                return False, False
            try:
                number = float(value)
            except (ValueError, TypeError):
                return False, False
            # API uses -1 as a placeholder for missing/IFRS revenue
            if number < 0:
                return False, envelope.get('reference_year')
            return number, envelope.get('reference_year')

        revenue_value, revenue_year = extract_value(revenue)
        employees_value, employees_year = extract_value(employees)
        reference_year = revenue_year or employees_year

        return {
            'foretagssok_revenue_estimate': revenue_value,
            'foretagssok_employees_estimate': employees_value,
            'foretagssok_estimates_reference_year': reference_year,
        }

    def _foretagsapi_map_company(self, company):
        """Map a single company object to Odoo partner values."""
        if not company:
            return {}

        org_number = self._foretagsapi_format_org_number(company.get('orgNumber'))
        vat = self._foretagsapi_org_number_to_vat(company.get('orgNumber'))

        vals = {
            'name': company.get('name') or False,
            'company_registry': org_number,
            'vat': vat,
            'foretagssok_business_description': company.get('businessDescription') or False,
            'foretagssok_registration_date': self._foretagsapi_parse_date(company.get('registrationDate')),
            'foretagssok_deregistration_date': self._foretagsapi_parse_date(company.get('deregistrationDate')),
            'foretagssok_status': self._foretagsapi_map_status(company),
        }
        vals.update(self._foretagsapi_map_address(company))
        vals.update(self._foretagsapi_map_estimates(company))

        sni_records = self._foretagsapi_map_sni(company)
        if sni_records:
            vals['sni_id'] = sni_records[0].id
            vals['sni_ids'] = [(6, 0, sni_records.ids)]

        financials = self._foretagsapi_map_financials(company)
        if financials:
            vals['foretagssok_financial_ids'] = financials

        # Remove False/None values except for fields we explicitly want to clear
        return {k: v for k, v in vals.items() if v not in (False, None, '')}

    def _foretagsapi_map_status(self, company):
        parts = []
        if company.get('deregistrationDate'):
            parts.append(_('Deregistered'))
        if company.get('ongoingRestructuring'):
            parts.append(str(company['ongoingRestructuring']))
        if not parts:
            return _('Active')
        return ' / '.join(parts)
