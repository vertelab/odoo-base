from odoo import models, fields, api, _
import logging
import re

from allabolag.list import iter_list
from copy import deepcopy
from datetime import datetime
from urllib.parse import quote

from odoo.addons.partner_enrich_base.models.enrich_format import (
    empty,
    pick,
    to_float,
    to_int,
)


_logger = logging.getLogger(__name__)
COMPANY_NO_IAP = True

#: The key this provider registers under in ``partner_enrich.provider_order``.
PROVIDER_KEY = 'allabolag'


class ResPartnerMixin(models.AbstractModel):
    _name = "res.partner.allabolag.mixin"
    _description = """
        Mixin class for Allabolag-information
    
    """

    kpi_no_employees = fields.Char(string='Number of employees')
    kpi_revenue_employees = fields.Float(string='Revenue per Employee')
    linkTo = fields.Char(string='Link', help="Link to Allabolag")
    remarkCode = fields.Char(string='Remark', size=4)
    remarkDate = fields.Date(string='Remark Date') # fields.date.add|context_today|end_of|start_of|substract|to_date|to_string|today
    remarkDescription = fields.Char(string='Remark Descr', trim=True, )
    summary_cash_flow = fields.Float(string='Cash Flow')
    summary_net_sales_change = fields.Float(string='Net Sales Changes')
    summary_parent_company = fields.Char(string='Parent Company')
    summary_profit_ebit = fields.Float(string='Profit EBIT KSEK')
    summary_profit_margin = fields.Float(string='Profit Margin')
    summary_purpose = fields.Text(string='Business and purpose')
    summary_registry_year = fields.Date(string='Registry Year')
    summary_revenue = fields.Float(string='Revenue KSEK')
    summary_solvency = fields.Float(string='Solvency')
    summary_state = fields.Char(string='Business status')
    
    @api.model
    def name2orgno(self,name):
        name = quote(name)
        i = 1
        for item in iter_list(
            f"what/{name}/xs/1",
            # ~ lambda x: _parse_liquidated_company_item(x)["Konkurs inledd"] < until,
            ):
            print(item.keys())
            i += 1
            if i > 1:
                break 
        if i == 1:
            return None,None
        _logger.warning(f'{item=}')
        
        return item['orgnr'],item
        

class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = ['res.partner', 'res.partner.allabolag.mixin']

    def check_bankruptcy(self):
        until = datetime.strptime('2024-07-01','%Y-%m-%d') #TODO fetch this date from system parameter
        orgnummer=[]
        
        def _parse_liquidated_company_item(item_dict):
            
            item = deepcopy(item_dict)

            # store for backward compability
            item["link"] = item_dict["linkTo"]
            item["Org.nummer"] = item_dict["orgnr"]

            for remark in item_dict["remarks"]:
                key = remark["remarkDescription"]  # ie. Konkurs inledd
                if remark["remarkDate"] is not None:
                    item[key] = datetime.strptime(remark["remarkDate"], "%Y-%m-%d")
                # TODO: Handle other remarks such as:
                # 'remarkCode': 'SHV',
                # 'remarkDescription': 'Svensk Handel Varningslistan med produktnamn: registersök.',
                # 'remarkDate': None,

            return item
        
        i = 1
        for item in iter_list(
                "/lista/konkurs-inledd/6",
                # ~ lambda x: _parse_liquidated_company_item(until=until),
                lambda x: _parse_liquidated_company_item(x)["Konkurs inledd"] < until,
            ):
            orgnummer.append(item['orgnr'])
            i += 1
            if i > 1000:
                break 
        _logger.warning(f'{orgnummer}')
        
        for partner in self.env['res.partner'].search([('company_registry', 'in', orgnummer )]):
            partner.message_post(
                body=_('Company filed for bankruptcy'),
                message_type='notification',
            )
        
        #TODO save todays date to system parameter

    # ---------------------------------------------------------------------
    # Provider contract
    # ---------------------------------------------------------------------

    @api.model
    def _enrich_from_provider(self, provider_key, ctx):
        """Answer the base module's provider call for ``allabolag``."""
        if provider_key != PROVIDER_KEY:
            return super()._enrich_from_provider(provider_key, ctx)
        mode = ctx.get('mode') or 'enrich'
        try:
            if mode == 'search':
                return self._allabolag_search(ctx)
            if mode == 'detail':
                return self._allabolag_detail(ctx)
            return self._allabolag_enrich(ctx)
        except ImportError:
            _logger.info(
                "The 'allabolag' Python package is not installed — the "
                "allabolag provider is disabled.",
            )
            return [] if mode == 'search' else {}
        except Exception:  # noqa: BLE001 - a scrape failure is not fatal
            _logger.warning(
                "Allabolag lookup failed (mode=%s).", mode, exc_info=True,
            )
            return [] if mode == 'search' else {}

    @api.model
    def _allabolag_search(self, ctx):
        """One scrape, by organisation number or by name.

        ``name2orgno()`` is the only search Allabolag offers us, and it costs a
        full page fetch. It is therefore called at most once per lookup.
        """
        registry = ctx.get('registry')
        if empty(registry):
            name = ctx.get('name')
            if empty(name):
                return []
            registry, _item = self.name2orgno(name)
        if empty(registry):
            return []
        canonical = self._allabolag_fetch(registry)
        return [canonical] if canonical else []

    @api.model
    def _allabolag_detail(self, ctx):
        reference = ctx.get('reference')
        if empty(reference):
            return {}
        return self._allabolag_fetch(reference) or {}

    @api.model
    def _allabolag_enrich(self, ctx):
        registry = ctx.get('registry')
        if empty(registry):
            name = ctx.get('name')
            if empty(name):
                return {}
            registry, _item = self.name2orgno(name)
        if empty(registry):
            return {}
        return self._allabolag_fetch(registry) or {}

    # ---------------------------------------------------------------------
    # Fetch and map
    # ---------------------------------------------------------------------

    @api.model
    def _allabolag_fetch(self, registry):
        """Fetch one company and map it to the canonical format."""
        from allabolag import Company
        from allabolag.company import NoSuchCompany

        digits = ''.join(ch for ch in str(registry) if ch.isdigit())
        if len(digits) != 10:
            _logger.info("Allabolag: %r is not an organisation number.", registry)
            return {}
        try:
            company = Company('%s-%s' % (digits[:6], digits[6:]))
            data = company.data
        except NoSuchCompany:
            _logger.info("Allabolag has no company %s.", digits)
            return {}
        if not data:
            return {}
        return self._allabolag_map_company(data)

    @api.model
    def _allabolag_map_company(self, data):
        """Map ``Company.data`` onto the canonical enrichment format.

        The organisation number is passed through raw; the base module
        normalises it. Financial figures arrive in SEK from Allabolag and are
        converted to the same unit the other providers use (whole kronor).
        """
        company = (data or {}).get('company') or {}
        if not company:
            return {}
        address = company.get('postalAddress') or {}
        status = company.get('status') or {}
        contact = company.get('contactPerson') or {}

        canonical = {
            'name': pick(company, 'name'),
            'company_registry': pick(company, 'orgnr'),
            'legal_form': pick(company, 'legalForm', 'companyForm'),
            'status': pick(status, 'status') or False,
            'registration_date': self._allabolag_parse_date(
                company.get('registrationDate')),
            'street': pick(address, 'addressLine'),
            'street2': pick(address, 'addressLine2'),
            'zip': pick(address, 'zipCode'),
            'city': pick(address, 'postPlace'),
            # Allabolag is a Swedish register; the country is implicit.
            'country_code': 'SE',
            'phone': pick(company, 'phone'),
            'mobile': pick(company, 'mobile'),
            'email': pick(company, 'email'),
            'website': pick(company, 'homePage'),
            'sni_codes': self._allabolag_sni_codes(company),
            'financials': self._allabolag_financials(company),
            'payload': company,
        }
        # ``contactPerson`` is a person, not a company field. It is kept in the
        # payload so a caller can use it; writing it into ``name`` would
        # overwrite the company name with a human's.
        if contact:
            canonical['payload'] = dict(company, _contact=contact)
        return canonical

    @api.model
    def _allabolag_parse_date(self, value):
        from odoo import fields

        if empty(value):
            return False
        try:
            return fields.Date.to_date(value)
        except (ValueError, TypeError):
            return False

    @api.model
    def _allabolag_sni_codes(self, company):
        codes = []
        for key in ('sniCode', 'sniCodes', 'sni'):
            value = company.get(key)
            if empty(value):
                continue
            if isinstance(value, (list, tuple)):
                codes.extend(str(code).strip() for code in value if not empty(code))
            elif isinstance(value, dict):
                codes.extend(
                    str(code).strip() for code in value.values() if not empty(code)
                )
            else:
                codes.append(str(value).strip())
        # Deduplicate while keeping order.
        return list(dict.fromkeys(codes))

    @api.model
    def _allabolag_financials(self, company):
        """One canonical financials entry from the overview figures.

        Allabolag's overview gives a single latest-year snapshot, not a series.
        ``fiscal_year`` is therefore derived from the accounts year when it is
        present, and left out otherwise — a financial row with a guessed year is
        worse than a row without one.
        """
        entry = {
            'net_sales': to_float(company.get('revenue')),
            'operating_profit': to_float(company.get('profit')),
            'employees': to_int(company.get('employees')),
        }
        year = pick(company, 'accountFiguresYear', 'accountsYear')
        if not empty(year):
            entry['fiscal_year'] = str(to_int(year) or year)
        entry = {key: value for key, value in entry.items() if not empty(value)}
        return [entry] if entry else []

    # ---------------------------------------------------------------------
    # Provider-specific fields
    # ---------------------------------------------------------------------

    def _enrich_apply_extra(self, resolved, collected):
        """Map the ``summary_*`` / ``kpi_*`` fields Allabolag owns."""
        vals = super()._enrich_apply_extra(resolved, collected)
        if not any(pkey == PROVIDER_KEY for _v, pkey in resolved.values()):
            return vals
        canonical = dict(collected).get(PROVIDER_KEY) or {}
        company = canonical.get('payload') or {}
        if not company:
            return vals

        revenue = to_float(company.get('revenue'))
        employees = to_int(company.get('employees'))
        if not employees and revenue:
            # Allabolag leaves employees at 0 for many small companies. A
            # revenue-derived estimate is better than a blank, but it is
            # recorded as an estimate, never as a reported figure.
            employees = max(1, int(revenue // 200000))
        purpose = pick(company, 'purpose')
        contact = company.get('_contact') or {}

        extra = {
            'summary_revenue': revenue,
            'summary_profit_ebit': to_float(company.get('profit')),
            'summary_purpose': purpose,
            'summary_state': pick(company.get('status') or {}, 'status'),
            'summary_registry_year': self._allabolag_parse_date(
                company.get('registrationDate')),
            'summary_parent_company': pick(company, 'parentCompany'),
            'kpi_no_employees': employees,
            'kpi_revenue_employees': (
                round(revenue / employees, 2) if employees and revenue else False
            ),
            'linkTo': pick(company, 'linkTo', 'url'),
            'remarkCode': pick(company, 'remarkCode'),
            'remarkDescription': pick(company, 'remarkDescription'),
            'remarkDate': self._allabolag_parse_date(company.get('remarkDate')),
            'contact_name': pick(contact, 'name'),
            'function': pick(contact, 'role'),
        }
        for key, value in extra.items():
            if not empty(value):
                vals[key] = value
        return vals
