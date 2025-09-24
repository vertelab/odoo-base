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

    def _get_booking_slots(self, timezone, filter_users=None, filter_resources=None, asked_capacity=1, reference_date=None):
        slots = super()._get_booking_slots(timezone, filter_users, filter_resources, asked_capacity, reference_date)

        if self.booking_type != 'boat':
            return slots

        for month in slots:
            for week in month.get('weeks', []):
                for day in week:
                    if not day.get('slots'):
                        continue
                    for slot in day.get('slots'):
                        if not slot.get('available_resources'):
                            continue
                        
                        resource_ids = [r['id'] for r in slot['available_resources']]
                        if not resource_ids:
                            continue

                        resources_data = self.env['booking.resource'].search_read(
                            [('id', 'in', resource_ids)],
                            ['id', 'name', 'capacity', 'latitude', 'longitude', 'length', 'width', 'depth']
                        )
                        
                        resources_map = {res['id']: res for res in resources_data}
                        
                        detailed_resources = []
                        for res_info in slot['available_resources']:
                            res_id = res_info['id']
                            if res_id in resources_map:
                                detailed_resources.append(resources_map[res_id])
                        
                        slot['available_resources'] = detailed_resources
        
        return slots
