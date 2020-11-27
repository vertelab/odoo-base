from odoo import models, fields


class ResPartnerEducationLevel(models.Model):
    _name = "res.partner.education_level"

    name = fields.Integer(string="Education level")
    partner_ids = fields.One2many(comodel_name="res.partner",
                                  inverse_name="education_level")
    description = fields.Char(string="Description")
