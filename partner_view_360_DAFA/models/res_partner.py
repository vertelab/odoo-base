from odoo import models, api, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    jobseeker_category_id = fields.Many2one(comodel_name='res.partner.skat')
    jobseeker_category = fields.Char(string="Jobseeker category", compute="combine_category_name_code")

    @api.multi
    def combine_category_name_code(self):
        for rec in self:
            if rec.jobseeker_category_id:
                rec.jobseeker_category = "%s %s" % (rec.jobseeker_category_id.name, rec.jobseeker_category_id.code)

class ResPartnerSKAT(models.Model):
    _name = "res.partner.skat"
    _description = "RES PARTNER SKAT"

    partner_id = fields.One2many(
        comodel_name="res.partner", inverse_name="jobseeker_category_id"
    )
    code = fields.Char(string="code")
    name = fields.Char(string="name")