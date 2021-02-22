from odoo import models, fields, api


class ResPartnerEducationLevel(models.Model):
    _name = "res.partner.education.education_level"
    _description = """Value store for education level."""

    name = fields.Integer(string="Education level")
    description = fields.Char(string="Description")

    @api.multi
    def name_get(self):
        res = super(ResPartnerEducationLevel, self).name_get()
        data = []
        for edu_lvl in self:
            display_value = ''
            display_value += edu_lvl.description or ""
            display_value += ' ('
            display_value += edu_lvl.name or ""
            display_value += ')'
            data.append((edu_lvl.id, display_value))
        return data
