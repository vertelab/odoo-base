from odoo import models, api, _, fields
from odoo.exceptions import UserError


class ProjectTask(models.Model):
    _inherit = 'project.task'

    report_date = fields.Char(string='Report Date', readonly=True)

    def action_send_serp_report(self):
        self.ensure_one()

        if not self.partner_id:
            raise UserError(_('No partner set on this task'))

        if not self.partner_id.email:
            raise UserError(_('Partner has no email address'))

        template_id = self.env.ref('base_serp.email_template_serp_report').id
        
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': {
                'default_model': 'project.task',
                'default_res_ids': [self.id],
                'default_use_template': True,
                'default_template_id': template_id,
                'default_composition_mode': 'comment',
                'mark_so_as_sent': True,
                'custom_layout': "mail.mail_notification_light",
                'force_email': True,
            },
        }

    def action_preview_serp_report(self):
        self.ensure_one()
        return self.env.ref('base_serp.action_report_serp_pdf').report_action(self)
