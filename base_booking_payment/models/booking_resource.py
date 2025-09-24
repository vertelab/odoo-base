from odoo import models, fields, api, _

class BookingResource(models.Model):
    _inherit = "booking.resource"

    product_id = fields.Many2one("product.product", string="Product")

