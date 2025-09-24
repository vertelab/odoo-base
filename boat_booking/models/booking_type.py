from odoo import models, fields, api, _
from odoo.http import request

class BookingType(models.Model):
    _inherit = "booking.type"

    product_id = fields.Many2one("product.product", string="Product")
    booking_type = fields.Selection([
        ('boat', 'Boat'),
        ('other', 'Other')
    ], string="Type", default="other")

    def _prepare_calendar_event_values(
        self, asked_capacity, booking_line_values, duration,
        booking_invite, guests, name, customer, staff_user, start, stop
    ):
        values = super()._prepare_calendar_event_values(
            asked_capacity, booking_line_values, duration,
            booking_invite, guests, name, customer, staff_user, start, stop
        )
        # Propagate boat dimensions from website params, like base_booking does for other fields
        try:
            params = getattr(request, 'params', {}) or {}
        except Exception:
            params = {}

        def _flt(key):
            try:
                v = params.get(key)
                return float(v) if v not in (None, '', False) else None
            except Exception:
                return None

        L = _flt('length'); W = _flt('width'); D = _flt('depth')
        if L is not None:
            values['length'] = L
        if W is not None:
            values['width'] = W
        if D is not None:
            values['depth'] = D

        return values
