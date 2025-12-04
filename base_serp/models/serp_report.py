# models/serp_report.py
# -*- coding: utf-8 -*-
from odoo import models, fields, api


class SerpReport(models.Model):
    _name = 'serp.report'
    _description = 'SERP Report'
    _inherit = ['website.published.mixin']  # Add website mixin
    _order = 'create_date desc'

    name = fields.Char(string='Report Name', compute='_compute_name', store=True)
    partner_id = fields.Many2one('res.partner', string='Partner', required=True, ondelete='cascade')
    date_from = fields.Date(string='From Date', required=True)
    date_to = fields.Date(string='To Date', required=True)
    graph_html = fields.Html(string='Graph HTML', sanitize=False)
    website_page_id = fields.Many2one('website.page', string='Website Page', readonly=True)  # Add this

    @api.depends('partner_id', 'date_from', 'date_to')
    def _compute_name(self):
        for report in self:
            report.name = f"{report.partner_id.name} - {report.date_from} to {report.date_to}"

    def _compute_website_url(self):
        """Override website mixin to provide custom URL"""
        for report in self:
            report.website_url = f'/serp-report/{report.id}'