# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = ['res.partner', 'serp.mixin']

    @api.onchange('website')
    def _onchange_website_serp(self):
        """Auto-populate serp_domain from website field"""
        if self.website and not self.serp_domain:
            # Extract domain from URL
            domain = self.website
            # Remove http://, https://, www.
            domain = domain.replace('http://', '').replace('https://', '').replace('www.', '')
            # Remove trailing slash
            domain = domain.rstrip('/')
            # Take only domain part (before first /)
            domain = domain.split('/')[0]

            self.serp_domain = domain

