from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import SQL


class UserLookupWizard(models.TransientModel):
    _name = 'user.lookup.wizard'
    _description = 'User Lookup Wizard'
    _transient_max_count = 0
    _transient_max_hours = 24

    old_user_id = fields.Many2one('res.users', string="Old User", required=True)
    new_user_id = fields.Many2one('res.users', string="New User", required=True)
    line_ids = fields.One2many('user.lookup.wizard.line', 'wizard_id')
    line_count = fields.Integer(compute='_compute_line_count')

    def _compute_display_name(self):
        self.display_name = _('User Lookup')

    @api.depends('line_ids')
    def _compute_line_count(self):
        for wizard in self:
            wizard.line_count = len(wizard.line_ids)

    def _get_query_models_blacklist(self):
        return [
            'res.users',
            'mail.notification',
            'mail.followers',
            'discuss.channel.member',
            'res.users.settings',
        ]

    def _get_query(self):
        self.ensure_one()

        if not self.old_user_id:
            raise UserError(_('Please select an old user'))

        old_user_id = self.old_user_id.id
        blacklisted_models = self._get_query_models_blacklist()
        query_parts = []

        for model_name in self.env:
            if model_name in blacklisted_models:
                continue

            model = self.env[model_name]

            if model._transient or not model._auto:
                continue

            # Check if model has user_id field
            if 'user_id' not in model._fields:
                continue

            field = model._fields['user_id']
            if field.comodel_name != 'res.users' or not field.store or field.type != 'many2one':
                continue

            table_name = model._table
            model_id = self.env['ir.model'].search([('model', '=', model_name)], limit=1).id

            query_parts.append(SQL(
                """
                SELECT
                    %s AS res_model_id,
                    id AS res_id
                FROM %s
                WHERE user_id = %s
                """,
                model_id,
                SQL.identifier(table_name),
                old_user_id,
            ))

        if not query_parts:
            return SQL("SELECT NULL::integer AS res_model_id, NULL::integer AS res_id WHERE FALSE")

        return SQL("\n UNION ALL \n").join(query_parts)

    def action_user_lookup(self):
        self.ensure_one()
        query = self._get_query()
        self.env.flush_all()
        self.env.cr.execute(query)
        results = self.env.cr.dictfetchall()
        self.line_ids = [(5, 0, 0)] + [(0, 0, reference) for reference in results]
        return self.action_open_lines()

    def action_replace_all_users(self):
        self.ensure_one()

        if not self.new_user_id:
            raise UserError(_('Please select a new user'))

        if self.old_user_id.id == self.new_user_id.id:
            raise UserError(_('Old user and new user cannot be the same'))

        count = 0
        for line in self.line_ids:
            if line.is_updated:
                continue
            try:
                record = self.env[line.res_model].sudo().browse(line.res_id)
                if record.exists() and hasattr(record, 'user_id'):
                    record.write({'user_id': self.new_user_id.id})
                    line.is_updated = True
                    count += 1
            except Exception:
                pass

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('%s records updated') % count,
                'type': 'success',
                'sticky': False,
            }
        }

    def action_open_lines(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id(
            'base_replace_user.action_user_lookup_wizard_line'
        )
        action['domain'] = [('wizard_id', '=', self.id)]
        return action