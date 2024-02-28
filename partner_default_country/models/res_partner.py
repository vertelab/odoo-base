from odoo import models, fields, api, _


class Partner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def _set_default_country(self):
        return self.env.company.country_id.id

    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict', default=_set_default_country)
