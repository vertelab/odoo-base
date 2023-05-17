from odoo import models, fields, api, _


class ProjectEstimate(models.Model):
    _inherit = "project.estimate"

    project_id = fields.Many2one("project.project", string="Project")

