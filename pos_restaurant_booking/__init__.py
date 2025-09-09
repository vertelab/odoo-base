# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from . import models

def _pos_restaurant_booking_after_init(env):
    table_ids = env['restaurant.table'].search([('booking_resource_id', '=', False)])
    for table_id in table_ids:
        table_id.booking_resource_id = table_id.env['booking.resource'].sudo().create({
            'name': f'{table_id.floor_id.name} - {table_id.table_number}',
            'capacity': table_id.seats,
            'pos_table_ids': table_id,
        })
