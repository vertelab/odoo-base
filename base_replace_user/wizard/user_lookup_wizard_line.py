from odoo import models, fields, api, _
from odoo.exceptions import UserError


class UserLookupWizardLine(models.TransientModel):
    _name = 'user.lookup.wizard.line'
    _description = 'User Lookup Wizard Line'
    _transient_max_count = 0
    _transient_max_hours = 24

    @api.model
    def _selection_target_model(self):
        return [(model.model, model.name) for model in self.env['ir.model'].sudo().search([])]

    wizard_id = fields.Many2one('user.lookup.wizard', required=True, ondelete='cascade')
    res_id = fields.Integer(string="Resource ID", required=True)
    res_name = fields.Char(string='Resource name', compute='_compute_res_name', store=True)
    res_model_id = fields.Many2one('ir.model', 'Related Document Model', ondelete='cascade')
    res_model = fields.Char(string='Document Model', related='res_model_id.model', store=True, readonly=True)
    resource_ref = fields.Reference(
        string='Record',
        selection='_selection_target_model',
        compute='_compute_resource_ref',
        inverse='_set_resource_ref'
    )
    is_updated = fields.Boolean(default=False, string="Updated")

    @api.depends('res_model', 'res_id', 'is_updated')
    def _compute_resource_ref(self):
        for line in self:
            if line.res_model and line.res_model in self.env:
                try:
                    self.env[line.res_model].browse(line.res_id).check_access('read')
                    line.resource_ref = '%s,%s' % (line.res_model, line.res_id or 0)
                except Exception:
                    line.resource_ref = None
            else:
                line.resource_ref = None

    def _set_resource_ref(self):
        for line in self:
            if line.resource_ref:
                line.res_id = line.resource_ref.id

    @api.depends('res_model', 'res_id')
    def _compute_res_name(self):
        for line in self:
            if not line.res_id or not line.res_model:
                continue
            record = self.env[line.res_model].sudo().browse(line.res_id)
            if not record.exists():
                continue
            name = record.display_name
            line.res_name = name if name else f'{line.res_model_id.name}/{line.res_id}'

    def action_open_record(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_id': self.res_id,
            'res_model': self.res_model,
        }

    def action_update_user(self):
        """Update user_id for selected lines (works for single or bulk)"""
        if not self:
            raise UserError(_('No records selected'))

        # Get the wizard (should be the same for all lines)
        wizard = self[0].wizard_id

        if not wizard.new_user_id:
            raise UserError(_('Please select a new user in the wizard'))

        if wizard.old_user_id.id == wizard.new_user_id.id:
            raise UserError(_('Old user and new user cannot be the same'))

        success_count = 0
        error_count = 0
        already_updated = 0

        for line in self:
            if line.is_updated:
                already_updated += 1
                continue

            try:
                record = self.env[line.res_model].sudo().browse(line.res_id)
                if not record.exists():
                    error_count += 1
                    continue

                if not hasattr(record, 'user_id'):
                    error_count += 1
                    continue

                record.write({'user_id': wizard.new_user_id.id})
                line.is_updated = True
                success_count += 1
            except Exception as e:
                error_count += 1
                continue

        # Build notification message
        messages = []
        if success_count:
            messages.append(_('%s records updated') % success_count)
        if already_updated:
            messages.append(_('%s already updated') % already_updated)
        if error_count:
            messages.append(_('%s failed') % error_count)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('User Update Complete'),
                'message': ', '.join(messages),
                'type': 'success' if error_count == 0 else 'warning',
                'sticky': False,
            }
        }