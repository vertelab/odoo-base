from odoo import fields, api, models, _


class Website(models.Model):
    _inherit = "website"

    map_id = fields.Char(string="Map ID")