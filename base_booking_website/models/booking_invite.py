# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.tools import format_list


class BookingAppointmentType(models.Model):
    _name = "booking.invite"
    _inherit = ['booking.invite', 'website.published.multi.mixin']

    booking_type_warning_msg = fields.Char('Different Website Message', compute='_compute_booking_type_warning_msg')

    @api.depends('booking_type_warning_msg')
    def _compute_disable_save_button(self):
        super()._compute_disable_save_button()
        for invite in self:
            invite.disable_save_button = invite.disable_save_button or bool(invite.booking_type_warning_msg)

    @api.depends('booking_type_ids', 'website_id')
    def _compute_booking_type_warning_msg(self):
        """ When a particular website is selected, display an alert warning to tell the current user that the website selected and the booking types are not compatible. """
        self.booking_type_warning_msg = False
        for invite in self.filtered('website_id'):
            appt_with_different_website = invite.booking_type_ids.filtered_domain([('website_id', 'not in', [False, invite.website_id.id])])
            if len(appt_with_different_website) > 0:
                invite.booking_type_warning_msg = _(
                    "The following booking type(s) are not compatible with the website chosen: %(bookings)s",
                    bookings=format_list(self.env, appt_with_different_website.mapped("name")),
                )

    @api.depends('short_code', 'website_id')
    def _compute_base_book_url(self):
        super()._compute_base_book_url()
