from odoo import Command, fields, http
from odoo.http import request
from odoo.addons.base_booking.controllers.booking import BookingController
from odoo.addons.base_booking_payment.controllers.booking import BookingAccountPayment
from odoo.addons.base.models.ir_qweb import keep_query
from odoo.tools.misc import get_lang


class BoatBookingControllerExtended(BookingAccountPayment):

    def _calendar_booking_values(
            self, booking_type, selected_resource, date_start, date_end, duration, answer_input_values, name, customer,
            booking_invite, guests=None, staff_user=None, asked_capacity=1, booking_line_values=None):
        values = {
            'booking_answer_input_ids': [Command.create(vals) for vals in answer_input_values],
            'booking_invite_id': booking_invite.id,
            'booking_type_id': booking_type.id,
            'booking_line_ids': [Command.create(vals) for vals in booking_line_values],
            'asked_capacity': asked_capacity,
            'guest_ids': [Command.link(pid) for pid in guests.ids] if guests else [],
            'name': name,
            'partner_id': customer.id,
            'staff_user_id': staff_user.id,
            'start': date_start,
            'stop': date_end,
        }
        if booking_type.schedule_based_on == 'users':
            values['product_id'] = booking_type.product_id.id
        elif booking_type.schedule_based_on == 'resources':
            if booking_type.booking_type == 'boat' and selected_resource.product_id:
                values["product_id"] = selected_resource.product_id.id
            else:
                values['product_id'] = booking_type.product_id.id
        return values

    def _handle_booking_form_submission(self, booking_type, selected_resource, date_start, date_end, duration, answer_input_values, name, customer, booking_invite, guests=None, staff_user=None, asked_capacity=1, booking_line_values=None):
        if (booking_type.has_payment_step and booking_type.product_id.lst_price) or (selected_resource and selected_resource.product_id.lst_price):
            calendar_booking = request.env['calendar.booking'].sudo().create([self._calendar_booking_values(
                booking_type=booking_type,
                selected_resource=selected_resource,
                date_start=date_start, date_end=date_end,
                duration=duration, answer_input_values=answer_input_values, name=name,
                customer=customer, booking_invite=booking_invite, guests=guests, staff_user=staff_user,
                asked_capacity=asked_capacity, booking_line_values=booking_line_values
            )])
            return self._redirect_to_payment(calendar_booking)

        return super()._handle_booking_form_submission(booking_type, selected_resource, date_start, date_end, duration, answer_input_values, name, customer, booking_invite, guests, staff_user, asked_capacity, booking_line_values)