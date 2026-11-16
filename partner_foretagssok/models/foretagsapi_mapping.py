# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

"""Map FöretagsAPI.se responses onto the canonical enrichment format.

The old ``_foretagsapi_map_company()`` returned ready-to-write Odoo values,
including ``foretagssok_*`` fields and a ``(0, 0, {...})`` command list for the
financials one2many. Two things were wrong with that:

1. It normalised the organisation number itself (``NNNNNN-NNNN``), which is how
   the same company ended up with three different formats depending on which
   provider ran first.
2. It could not be combined with another provider, because it had already
   decided what to write.

This module maps to the canonical dict instead. Normalisation happens once, in
``partner_enrich_base``; writing happens once, after the policy has chosen a
winner per field group.
"""

import logging

from odoo import _, fields, models

from odoo.addons.partner_enrich_base.models.enrich_format import (
    FINANCIAL_FIELDS,
    empty,
    pick,
    to_float,
    to_int,
)

_logger = logging.getLogger(__name__)


class ForetagsapiMappingMixin(models.AbstractModel):
    """Helper mixin that maps FöretagsAPI.se responses to canonical dicts."""

    _name = 'foretagsapi.mapping.mixin'
    _description = 'FöretagsAPI Response Mapping'

    # -- small parsers ------------------------------------------------------

    def _foretagsapi_parse_date(self, value):
        if empty(value):
            return False
        try:
            return fields.Date.to_date(value)
        except (ValueError, TypeError):
            return False

    def _foretagsapi_map_status(self, company):
        parts = []
        if company.get('deregistrationDate'):
            parts.append(str(_('Deregistered')))
        if company.get('ongoingRestructuring'):
            parts.append(str(company['ongoingRestructuring']))
        if not parts:
            return str(_('Active'))
        return ' / '.join(parts)

    # -- canonical mapping --------------------------------------------------

    def _foretagsapi_map_address(self, company):
        address = company.get('postalAddress') or {}
        return {
            'street': pick(address, 'street', 'addressLine1'),
            'street2': pick(address, 'street2', 'addressLine2'),
            'zip': pick(address, 'postalCode', 'zip'),
            'city': pick(address, 'city'),
            # FöretagsAPI is a Swedish register; the country is implicit.
            'country_code': 'SE',
        }

    def _foretagsapi_map_sni_codes(self, company):
        """Return the SNI codes as plain strings.

        Creating ``res.sni`` records is a side effect that belongs to the write
        step, not to the mapping — a mapping function that writes is a mapping
        function you cannot call twice.
        """
        sni_codes = company.get('sniCodes') or {}
        codes = []
        for index in range(1, 6):
            code = sni_codes.get('sni%s' % index)
            if empty(code) or code == '00000':
                continue
            codes.append(str(code).strip())
        return codes

    def _foretagsapi_map_financials(self, company):
        """Return the financials as a list of canonical dicts.

        Only keys in ``FINANCIAL_FIELDS`` are emitted; the base module's
        ``clean()`` would log anything else as a contract violation, and a
        provider should not be the thing that trips that warning.
        """
        financials = company.get('financials')
        if not financials:
            return []
        source = {
            'fiscal_year': financials.get('year'),
            'fiscal_year_start': self._foretagsapi_parse_date(
                financials.get('fiscalYearStart')),
            'fiscal_year_end': self._foretagsapi_parse_date(
                financials.get('fiscalYearEnd')),
            'net_sales': to_float(financials.get('revenue')),
            'operating_profit': to_float(financials.get('operatingResult')),
            'net_result': to_float(financials.get('netResult')),
            'result_after_financial_items': to_float(
                financials.get('resultAfterFinancialItems')),
            'profit_before_tax': to_float(financials.get('profitBeforeTax')),
            'total_assets': to_float(financials.get('totalAssets')),
            'equity': to_float(financials.get('equity')),
            'current_assets': to_float(financials.get('currentAssets')),
            'current_liabilities': to_float(
                financials.get('currentLiabilities')),
            'cash_and_bank': to_float(financials.get('cashAndBank')),
            'long_term_liabilities': to_float(
                financials.get('longTermLiabilities')),
            'fixed_assets': to_float(financials.get('fixedAssets')),
            'restricted_equity': to_float(financials.get('restrictedEquity')),
            'unrestricted_equity': to_float(
                financials.get('unrestrictedEquity')),
            'untaxed_reserves': to_float(financials.get('untaxedReserves')),
            'proposed_dividend': to_float(financials.get('proposedDividend')),
            'employees': to_int(financials.get('employees')),
            'solidity': to_float(financials.get('solidity')),
            'operating_margin': to_float(financials.get('operatingMargin')),
            'taxonomy': financials.get('taxonomy'),
            'currency': financials.get('currency'),
        }
        entry = {
            key: source[key]
            for key in FINANCIAL_FIELDS
            if not empty(source.get(key))
        }
        if not entry:
            return []
        if 'fiscal_year' in entry:
            entry['fiscal_year'] = str(entry['fiscal_year'])
        return [entry]

    def _foretagsapi_map_estimates(self, company):
        """Revenue and employee estimates, with their reference year.

        These are provider-specific fields, so they are *not* part of the
        canonical dict — they are returned separately and applied through
        ``_enrich_apply_extra()``.
        """
        def extract(envelope):
            if not envelope or envelope.get('type') == 'none':
                return False, False
            value = envelope.get('value')
            number = to_float(value)
            # The API uses -1 as a placeholder for "missing" (IFRS revenue).
            if number is False or number < 0:
                return False, envelope.get('reference_year')
            return number, envelope.get('reference_year')

        revenue_value, revenue_year = extract(
            company.get('revenue_estimate') or {})
        employees_value, employees_year = extract(
            company.get('employees_estimate') or {})
        return {
            'foretagssok_revenue_estimate': revenue_value,
            'foretagssok_employees_estimate': employees_value,
            'foretagssok_estimates_reference_year':
                revenue_year or employees_year,
        }

    def _foretagsapi_map_company(self, company):
        """Map one FöretagsAPI company object to a canonical dict.

        The organisation number is passed through *raw*; ``partner_enrich_base``
        normalises it. That is the whole point of the rewrite: one place
        decides what an organisation number looks like.
        """
        if not company:
            return {}
        canonical = {
            'name': pick(company, 'name', 'companyName'),
            'company_registry': pick(company, 'orgNumber', 'organizationNumber'),
            'legal_form': pick(company, 'legalForm', 'companyForm'),
            'status': self._foretagsapi_map_status(company),
            'registration_date': self._foretagsapi_parse_date(
                company.get('registrationDate')),
            'sni_codes': self._foretagsapi_map_sni_codes(company),
            'financials': self._foretagsapi_map_financials(company),
            'payload': company,
        }
        canonical.update(self._foretagsapi_map_address(company))
        # ``clean()`` in the base module drops the empties; doing it here as
        # well would mean two definitions of "empty" in the same code base.
        return canonical
