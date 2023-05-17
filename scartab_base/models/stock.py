from odoo import models, fields, api, _


class StockingPicking(models.Model):
    _inherit = "stock.picking"

    project_id = fields.Many2one("project.project", string="Project")

