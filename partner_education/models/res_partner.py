from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    education_ids = fields.One2many(string="Educations",
                                    comodel_name="res.partner.education",
                                    inverse_name="partner_id")
    cv = fields.Binary('CV')
    cv_file_name = fields.Char()
    references = fields.Binary()
    references_file_name = fields.Char()
    has_drivers_license = fields.Boolean(string="Has drivers license",
                                         compute='_compute_has_drivers_license')  # noqa 501
    drivers_license_ids = fields.Many2many(comodel_name='res.drivers_license',
                                           string='Drivers license class')
    has_car = fields.Boolean(string="Has access to car")

    @api.one
    def _compute_has_drivers_license(self):
        self.har_drivers_license = len(self.drivers_license_ids) > 0
