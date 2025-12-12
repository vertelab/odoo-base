from odoo import models, fields, api, _


class IrUiView(models.Model):
    _inherit = 'ir.ui.view'

    is_serp_view = fields.Boolean(string='Is Serp View')