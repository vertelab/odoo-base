from odoo import models, fields, api, _


class ResPartnerEducation(models.Model):
    _name = "res.partner.education"
    _description = "RES Partner Education"

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
        data = []
        for education in self:
            sun_code = education.sun_id.name or ""
            education_level = _("None")
            if education.education_level_id:
                education_level = education.education_level_id.name
            display_value = "".join((sun_code, ', ', str(education_level)))
            data.append((education.id, display_value))
        return data
