from odoo import models, api, _
from odoo.exceptions import UserError


class ProjectTask(models.Model):
    _inherit = 'project.task'

    def action_send_serp_report(self):
        """Open wizard to send SERP report email"""
        self.ensure_one()

        if not self.partner_id:
            raise UserError(_('No partner set on this task'))

        if not self.partner_id.email:
            raise UserError(_('Partner has no email address'))

        return {
            'type': 'ir.actions.act_window',
            'name': _('Send SERP Report'),
            'res_model': 'serp.report.send.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_task_id': self.id,
            },
        }