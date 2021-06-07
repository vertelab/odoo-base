from odoo import models, fields, api, _

class Ssyk(models.Model):

    _inherit = 'res.ssyk'

    demand_date = fields.Date("Demand Date")
    demand_value = fields.Float("Demand Value")
    previous_value = fields.Float("Previous Value")
    change_value = fields.Float("Change Value")
    change = fields.Float("Change(%)")
    previous_date = fields.Date("Previous Date")