# -*- coding: utf-8 -*-

from odoo import models, fields


class WebsiteAnalyticsReportType(models.Model):
    _inherit = 'website.analytics.report.type'

    api_module = fields.Selection([
        ('VisitsSummary', 'Visits Summary'),
        ('Actions', 'Actions (Pages, Downloads, etc.)'),
        ('Referrers', 'Referrers (Traffic Sources)'),
        ('UserCountry', 'User Country'),
        ('DevicesDetection', 'Devices Detection'),
        ('Resolution', 'Screen Resolution'),
        ('VisitorInterest', 'Visitor Interest'),
        ('CustomVariables', 'Custom Variables'),
    ], string='API Module', required=True)

    api_action = fields.Selection([
        ('get', 'Get'),
        ('getCountry', 'Get Country'),
        ('getPageUrls', 'Get Page URLs'),
        ('getAll', 'Get All'),
        ('getType', 'Get Type'),
        ('getBrand', 'Get Brand'),
        ('getBrowsers', 'Get Browsers'),
        ('getOsVersions', 'Get OS Versions'),
        ('getResolution', 'Get Resolution'),
    ], string='API Action', required=True)

    graph_type = fields.Selection([
        ('evolution', 'Evolution (Line Chart)'),
        ('verticalBar', 'Vertical Bar Chart'),
        ('pie', 'Pie Chart'),
        ('horizontalBar', 'Horizontal Bar Chart'),
    ], string='Graph Type', required=True, default='evolution')

    period = fields.Selection([
        ('day', 'Day'),
        ('week', 'Week'),
        ('month', 'Month'),
        ('year', 'Year'),
    ], string='Period', required=True, default='day')

    date = fields.Selection([
        ('today', 'Today'),
        ('yesterday', 'Yesterday'),
        ('lastWeek', 'Last Week'),
        ('lastMonth', 'Last Month'),
        ('lastYear', 'Last Year'),
        ('previous7', 'Previous 7'),
        ('previous30', 'Previous 30'),
        ('last7', 'Last 7'),
        ('last30', 'Last 30'),
    ], string='Date', required=True, default='previous30')

    last_n = fields.Integer(
        string='Last N',
        help='Number of periods to show (e.g., last 30 days, last 12 weeks). Leave 0 to disable.',
        default=0
    )

    width = fields.Integer(string='Width', default=800)
    height = fields.Integer(string='Height', default=300)
