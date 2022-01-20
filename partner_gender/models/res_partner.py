from odoo import fields, models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    gender = fields.Selection(
        [('male', _('Male')), ('female', _('Female')), ('other', _('Other')), ('decline', _('Decline to answer'))], default = 'other'
    )
    gender_txt = fields.Char()

    def calculate_gender(self):
        for partner in self:
            if partner.social_sec_nr:
                last_digit = int(partner.social_sec_nr[-2])
                if last_digit % 2 == 0:
                    partner.gender = 'female'
                else:
                    partner.gender = 'male'