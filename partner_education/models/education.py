from odoo import models, fields, api, _


class ResPartnerEducation(models.Model):
    _name = "res.partner.education"

    partner_id = fields.Many2one(comodel_name="res.partner")
    sun_id = fields.Many2one(comodel_name='res.sun',
                               string='SUN Code')
    education_level_id = fields.Many2one(
        comodel_name="res.partner.education.education_level",
        string="Education level")
    foreign_education = fields.Boolean(string="Foreign education")
    foreign_education_approved = fields.Boolean(
        string="Foreign education approved")

    @api.multi
    def name_get(self):
        res = super(ResPartnerEducation, self).name_get()
        data = []
        for education in self:
            sun_code = education.sun_id.name or ""
            education_level = education.education_level_id.name or _("None")
            display_value = "".join((sun_code, ', ', education_level))
            data.append((education.id, display_value))
        return data
