from odoo import fields, models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    gender = fields.Selection(
        [('male', _('Male')), ('female', _('Female')), ('other', _('Other')), ('decline', _('Decline to answer'))]
    )
    gender_txt = fields.Char()
