from odoo import models, fields, api, _


class UnbuildOrder(models.Model):
    _inherit = "sorting.order"

    project_id = fields.Many2one("project.project", string="Project")

