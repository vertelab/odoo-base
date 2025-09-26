import pytz

from babel.dates import format_datetime
from werkzeug.exceptions import NotFound

from odoo import Command, fields, http
from odoo.http import request
from odoo.addons.base_booking.controllers.booking import BookingController
from odoo.addons.base_booking_payment.controllers.booking import BookingAccountPayment
from odoo.addons.base.models.ir_qweb import keep_query
from odoo.addons.payment import utils as payment_utils
from odoo.tools.misc import get_lang


class BoatBookingControllerExtended(BookingAccountPayment):

    def _calendar_booking_type_values(
            self, booking_type, selected_resource, date_start, date_end, duration, answer_input_values, name,
            customer, booking_invite, guests=None, staff_user=None, asked_capacity=1, booking_line_values=None
    ):
        return {
            'booking_answer_input_ids': [Command.create(vals) for vals in answer_input_values],
            'booking_invite_id': booking_invite.id,
            'booking_type_id': booking_type.id,
            'booking_line_ids': [Command.create(vals) for vals in booking_line_values],
            'asked_capacity': asked_capacity,
            'guest_ids': [Command.link(pid) for pid in guests.ids] if guests else [],
            'name': name,
            'partner_id': customer.id,
            'product_id': booking_type.product_id.id or selected_resource.product_id.id,
            'staff_user_id': staff_user.id,
            'start': date_start,
            'stop': date_end,
        }

    def _calendar_booking_resource_values(
            self, booking_type, selected_resource, date_start, date_end, duration, answer_input_values, name,
            customer, booking_invite, guests=None, staff_user=None, asked_capacity=1, booking_line_values=None
    ):
        vals =  {
            'booking_answer_input_ids': [Command.create(vals) for vals in answer_input_values],
            'booking_invite_id': booking_invite.id,
            'booking_type_id': booking_type.id,
            'booking_line_ids': [Command.create(vals) for vals in booking_line_values],
            'asked_capacity': asked_capacity,
            'guest_ids': [Command.link(pid) for pid in guests.ids] if guests else [],
            'name': name,
            'partner_id': customer.id,
            'product_id': booking_type.product_id.id,
            'staff_user_id': staff_user.id,
            'start': date_start,
            'stop': date_end,
        }
        if booking_type.booking_type == 'boat' and selected_resource.product_id:
            vals["product_id"] = selected_resource.product_id.id
        return vals

    def _handle_booking_form_submission(
        self, booking_type, selected_resource,
        date_start, date_end, duration,
        answer_input_values, name, customer, booking_invite, guests=None,
        staff_user=None, asked_capacity=1, booking_line_values=None
    ):
        """ Override: when a payment step is necessary, we create the calendar booking model to store all relevant information
            instead of creating an calendar.event. This prevents synchronizing calendars with non-confirmed events. It will
            be transformed to a calendar.event on payment (or confirmation). See _make_event_from_paid_booking on calendar.booking.
            Redirects to payment if needed. See _redirect_to_payment"""
        if (booking_type.has_payment_step and booking_type.product_id.lst_price) or selected_resource.product_id.lst_price:
            calendar_booking = request.env['calendar.booking'].sudo().create([
                self._calendar_booking_type_values(
                    booking_type=booking_type,
                    selected_resource=selected_resource,
                    date_start=date_start, date_end=date_end,
                    duration=duration, answer_input_values=answer_input_values, name=name,
                    customer=customer, booking_invite=booking_invite, guests=guests, staff_user=staff_user,
                    asked_capacity=asked_capacity, booking_line_values=booking_line_values
                )
            ])
            return self._redirect_to_payment(calendar_booking)
        return super()._handle_booking_form_submission(
            booking_type, selected_resource, date_start, date_end, duration, answer_input_values, name,
            customer, booking_invite, guests, staff_user, asked_capacity, booking_line_values
        )