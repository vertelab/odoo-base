from odoo import models, fields, api, _

class CalendarEvent(models.Model):
    _inherit = "calendar.event"


    length = fields.Float(string="Length", readonly=True)
    width = fields.Float(string="Width", readonly=True)
    depth = fields.Float(string="Depth", readonly=True)
    