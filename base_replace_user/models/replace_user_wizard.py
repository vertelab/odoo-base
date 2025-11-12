from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ReplaceUserWizard(models.Model):
    _name = 'replace.user.wizard'
    _description = 'Replace User'

    old_user_id = fields.Many2one('res.users', string="Old User")
    new_user_id = fields.Many2one('res.users', string="New User")
    model_id = fields.Many2one('ir.model', string='Model', domain=[('transient', '=', False)])
    model_name = fields.Char(related='model_id.model', string='Model Name', readonly=True, store=True)
    domain = fields.Char(default="[]", help="Domain")

    def action_replace_user(self):
        domain = eval(self.domain) + [('user_id', '=', self.old_user_id.id)]
        record_ids = self.env[self.model_name].search(domain)
        if record_ids and self._verify_res_user_field():
            record_ids.write({'user_id': self.new_user_id.id})
        else:
            raise ValidationError(_(f'The model: {self.model_id.name} does not have a user_id field'))

    def _verify_res_user_field(self):
        user_field = self.model_id.field_id.filtered(
            lambda model: model.relation == 'res.users' and model.name == 'user_id'
        )
        return bool(user_field)
