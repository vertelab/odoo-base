from odoo import models, fields, api, _

class BookingResource(models.Model):
    _inherit = "booking.resource"

    address = fields.Char(string="Adress")
    street = fields.Char(string="Street")
    street2 = fields.Char(string="Street 2")
    city = fields.Char(string="City")
    zip = fields.Char(string="Zip")
    state_id = fields.Many2one("res.country.state", string="State")
    country_id = fields.Many2one("res.country", string="Country")

    longitude = fields.Float(string="Longitude")
    latitude = fields.Float(string="Latitude")
    length = fields.Float(string="Length")
    width = fields.Float(string="Width")
    depth = fields.Float(string="Depth")

