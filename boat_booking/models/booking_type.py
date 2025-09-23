from odoo import models, fields, api, _

class BookingType(models.Model):
    _inherit = "booking.type"

    product_id = fields.Many2one("product.product", string="Product")
    booking_type = fields.Selection([
        ('boat', 'Boat'),
        ('other', 'Other')
    ], string="Type", default="other")
