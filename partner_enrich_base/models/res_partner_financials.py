# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartnerFinancials(models.Model):
    """One fiscal year of a partner's key figures.

    Lives in the base module, not in a provider: the *shape* of a financial
    record is not provider-specific, and two providers writing the same company
    must land in the same rows. A provider that adds a figure not listed here
    keeps it in its own payload rather than inventing a parallel table.
    """

    _name = 'res.partner.financials'
    _description = 'Partner Financials'
    _order = 'fiscal_year desc'
    _rec_name = 'fiscal_year'

    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        required=True,
        ondelete='cascade',
        index=True,
    )
    fiscal_year = fields.Char(string='Fiscal Year', index=True)
    fiscal_year_start = fields.Date(string='Fiscal Year Start')
    fiscal_year_end = fields.Date(string='Fiscal Year End')
    taxonomy = fields.Char(string='Taxonomy')
    currency = fields.Char(string='Currency')

    net_sales = fields.Float(string='Net Sales')
    operating_profit = fields.Float(string='Operating Profit')
    net_result = fields.Float(string='Net Result')
    result_after_financial_items = fields.Float(
        string='Result After Financial Items')
    profit_before_tax = fields.Float(string='Profit Before Tax')
    total_assets = fields.Float(string='Total Assets')
    equity = fields.Float(string='Equity')
    current_assets = fields.Float(string='Current Assets')
    current_liabilities = fields.Float(string='Current Liabilities')
    cash_and_bank = fields.Float(string='Cash and Bank')
    long_term_liabilities = fields.Float(string='Long Term Liabilities')
    fixed_assets = fields.Float(string='Fixed Assets')
    restricted_equity = fields.Float(string='Restricted Equity')
    unrestricted_equity = fields.Float(string='Unrestricted Equity')
    untaxed_reserves = fields.Float(string='Untaxed Reserves')
    proposed_dividend = fields.Float(string='Proposed Dividend')
    employees = fields.Integer(string='Employees')
    solidity = fields.Float(string='Solvency')
    operating_margin = fields.Float(string='Operating Margin')

    _sql_constraints = [
        (
            'partner_fiscal_year_uniq',
            'unique(partner_id, fiscal_year)',
            'A partner can only have one financial record per fiscal year.',
        ),
    ]
