from odoo import http
from odoo.http import request


class BoatBookingController(http.Controller):
    
    @http.route('/boat_booking/locations', type='json', auth='public', website=True)
    def get_boat_locations(self, booking_type_id=False, min_length=None, min_width=None, min_depth=None, **kwargs):
        """Return grouped resource locations for a given booking type.

        Response format:
        [
            {
                'location_name': str,
                'lat': float,
                'lng': float,
                'resources': [{ 'id': int, 'name': str }]
            },
            ...
        ]
        """
        if not booking_type_id:
            return []


        booking_type = request.env['booking.type'].sudo().browse(int(booking_type_id)).exists()

        if not booking_type:
            return []

        # Parse filters
        def _flt(val):
            try:
                return float(val)
            except Exception:
                return None

        f_len = _flt(min_length)
        f_wid = _flt(min_width)
        f_dep = _flt(min_depth)

        # Build domain: attached to booking type and meets dimensions
        domain = [('id', 'in', booking_type.resource_ids.ids)]
        if f_len is not None and f_len > 0:
            domain.append(('length', '>=', f_len))
        if f_wid is not None and f_wid > 0:
            domain.append(('width', '>=', f_wid))
        if f_dep is not None and f_dep > 0:
            domain.append(('depth', '>=', f_dep))

        # Fetch resources via search to let DB filter
        resources = request.env['booking.resource'].sudo().search(domain)

        # Group by rounded coordinates to avoid floating point duplicates
        def _round_or_none(val):
            try:
                return round(float(val), 6)
            except Exception:
                return None

        locations = {}
        for res in resources:
            # Already filtered by the ORM domain above
            try:
                r_len = float(res.length) if res.length not in (None, False, '') else None
                r_wid = float(res.width) if res.width not in (None, False, '') else None
                r_dep = float(res.depth) if res.depth not in (None, False, '') else None
            except Exception:
                r_len = r_wid = r_dep = None
            lat = _round_or_none(res.latitude)
            lng = _round_or_none(res.longitude)
            if lat is None or lng is None:
                continue

            loc_key = (lat, lng)
            if loc_key not in locations:
                display = res.address or res.city or res.name or f"{lat}, {lng}"
                locations[loc_key] = {
                    'location_name': display,
                    'lat': lat,
                    'lng': lng,
                    'resources': [],
                }

            # Prepare pricing info if a product is linked
            price = None
            currency_symbol = None
            currency_position = None
            product = res.product_id
            if product:
                price = float(product.lst_price or 0.0)
                currency = product.currency_id or request.env.company.currency_id
                currency_symbol = currency.symbol
                currency_position = currency.position

            # Numeric dimensions if possible
            def _to_float_or_none(val):
                try:
                    return float(val)
                except Exception:
                    return None

            locations[loc_key]['resources'].append({
                'id': res.id,
                'name': res.name,
                'capacity': res.capacity,
                'length': r_len if r_len is not None else _to_float_or_none(res.length),
                'width': r_wid if r_wid is not None else _to_float_or_none(res.width),
                'depth': r_dep if r_dep is not None else _to_float_or_none(res.depth),
                'price': price,
                'currency_symbol': currency_symbol,
                'currency_position': currency_position,
                'book_url': f"/booking/{booking_type.id}?resource_selected_id={res.id}",
            })

        return list(locations.values())
