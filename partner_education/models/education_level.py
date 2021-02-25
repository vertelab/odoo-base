from odoo import models, fields, api


class ResPartnerEducationLevel(models.Model):
    _name = "res.partner.education.education_level"
    _description = """Value store for education level."""

    name = fields.Integer(string="Education level")
    description = fields.Char(string="Description")

    @api.multi
    def name_get(self):
        data = []
        for edu_lvl in self:
            description = edu_lvl.description or ""
            name = edu_lvl.name or "0"
            display_value = "".join((description, ' (', str(name), ')'))
            data.append((edu_lvl.id, display_value))
        return data
