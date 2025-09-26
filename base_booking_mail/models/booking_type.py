from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class BookingType(models.Model):
    _inherit = "booking.type"

    booking_mail_ids = fields.One2many(comodel_name="booking.mail",inverse_name="booking_type_id")


