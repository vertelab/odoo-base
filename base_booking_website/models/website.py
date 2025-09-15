# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, _


class Website(models.Model):
    _inherit = "website"

    def get_suggested_controllers(self):
        suggested_controllers = super(Website, self).get_suggested_controllers()
        suggested_controllers.append((_('Booking'), self.env['ir.http']._url_for('/booking'), 'base_booking_website'))
        return suggested_controllers

    def get_cta_data(self, website_purpose, website_type):
        cta_data = super(Website, self).get_cta_data(website_purpose, website_type)
        if website_purpose == 'schedule_bookings':
            cta_data.update({
                'cta_btn_text': _('Schedule an booking'),
                'cta_btn_href': '/booking',
            })
        return cta_data

    def _search_get_details(self, search_type, order, options):
        result = super()._search_get_details(search_type, order, options)
        if search_type in ['all', 'bookings']:
            result.append(self.env['booking.type']._search_get_detail(self, order, options))
        return result
