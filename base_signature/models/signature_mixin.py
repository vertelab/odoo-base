from odoo import models, fields


class SignatureMixin(models.AbstractModel):
    _name = 'signature.mixin'
    description = 'Sign on any Record'

    require_signature = fields.Boolean(string="Require Signature", default=False)
    signed_date = fields.Datetime(string="Signed Date")
    signature = fields.Binary(string="Signature")

