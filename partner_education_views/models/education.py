from odoo import models, fields, api


class ResPartnerEducation(models.Model):
    _name = "res.partner.education"

    sun_id = fields.Many2one(comodel_name='res.sun',
                               string='SUN Code')
    education_level_id = fields.Many2one(
        comodel_name="res.partner.education.education_level",
        string="Education level")
    foreign_education = fields.Boolean(string="Foreign education")
    foreign_education_approved = fields.Boolean(
        string="Foreign education approved")