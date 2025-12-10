# wizards/serp_report_send_wizard.py
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.misc import get_lang
from odoo import tools


class SerpReportSendWizard(models.TransientModel):
    _name = 'serp.report.send.wizard'
    _description = "SERP Report Send Wizard"

    task_id = fields.Many2one('project.task', string='Task', required=True, readonly=True)
    partner_id = fields.Many2one('res.partner', related='task_id.partner_id', readonly=True)

    # Mail fields
    mail_template_id = fields.Many2one(
        'mail.template',
        string="Email Template",
        domain="[('model', '=', 'project.task')]",
        compute='_compute_mail_template_id',
        readonly=False,
        store=True,
    )
    mail_lang = fields.Char(compute='_compute_mail_lang')
    mail_partner_ids = fields.Many2many(
        'res.partner',
        string="Recipients",
        compute='_compute_mail_fields',
        store=True,
        readonly=False,
    )
    mail_subject = fields.Char(
        string="Subject",
        compute='_compute_mail_fields',
        store=True,
        readonly=False,
    )
    mail_body = fields.Html(
        string="Contents",
        sanitize_style=True,
        compute='_compute_mail_fields',
        store=True,
        readonly=False,
    )
    mail_attachments_widget = fields.Json(
        compute='_compute_mail_attachments_widget',
        store=True,
        readonly=False,
    )

    # -------------------------------------------------------------------------
    # DEFAULTS
    # -------------------------------------------------------------------------

    @api.model
    def default_get(self, fields_list):
        results = super().default_get(fields_list)
        if 'task_id' in fields_list and 'task_id' not in results:
            task_id = self._context.get('active_id')
            if task_id:
                results['task_id'] = task_id
        return results

    # -------------------------------------------------------------------------
    # COMPUTE METHODS
    # -------------------------------------------------------------------------

    @api.depends('task_id')
    def _compute_mail_template_id(self):
        for wizard in self:
            wizard.mail_template_id = self.env.ref('base_serp.email_template_serp_report', raise_if_not_found=False)

    @api.depends('mail_template_id')
    def _compute_mail_lang(self):
        for wizard in self:
            if wizard.mail_template_id and wizard.task_id:
                wizard.mail_lang = wizard.mail_template_id._render_lang([wizard.task_id.id]).get(wizard.task_id.id)
            else:
                wizard.mail_lang = get_lang(self.env).code

    @api.depends('mail_template_id', 'mail_lang')
    def _compute_mail_fields(self):
        for wizard in self:
            if wizard.mail_template_id and wizard.task_id:
                wizard.mail_subject = wizard._get_mail_field_from_template('subject')

                # Get body from template
                mail_body = wizard._get_mail_field_from_template('body_html', options={'post_process': True})

                # Inject task description into the body
                # Find where to inject (look for the description placeholder)
                if wizard.task_id.description and mail_body:
                    # Replace the placeholder with actual description
                    mail_body = mail_body.replace(
                        '<t t-raw="object.description"/>',
                        wizard.task_id.description or ''
                    )

                wizard.mail_body = mail_body
                wizard.mail_partner_ids = wizard._get_default_mail_partners()
            else:
                wizard.mail_subject = wizard.mail_body = None
                wizard.mail_partner_ids = wizard.partner_id if wizard.partner_id.email else self.env['res.partner']

    @api.depends('task_id', 'mail_template_id')
    def _compute_mail_attachments_widget(self):
        """Build attachments widget data"""
        for wizard in self:
            # Keep manual attachments
            manual_attachments_data = [x for x in wizard.mail_attachments_widget or [] if x.get('manual')]

            # Get task attachments + template attachments
            wizard.mail_attachments_widget = (
                    wizard._get_task_attachments_data()
                    + wizard._get_mail_template_attachments_data()
                    + manual_attachments_data
            )

    # -------------------------------------------------------------------------
    # HELPERS
    # -------------------------------------------------------------------------

    def _get_mail_field_from_template(self, field, **kwargs):
        """Render a field from the mail template"""
        self.ensure_one()
        if not self.mail_template_id:
            return None
        return self.mail_template_id.with_context(lang=self.mail_lang)._render_field(
            field,
            self.task_id.ids,
            **kwargs
        )[self.task_id.id]

    def _get_default_mail_partners(self):
        """Get default mail partners from template"""
        self.ensure_one()

        partners = self.env['res.partner']

        if not self.mail_template_id:
            return self.partner_id if self.partner_id.email else partners

        # Get email_to
        if self.mail_template_id.email_to:
            email_to = self._get_mail_field_from_template('email_to')
            for mail_data in tools.email_split(email_to):
                partners |= partners.find_or_create(mail_data)

        # Get email_cc
        if self.mail_template_id.email_cc:
            email_cc = self._get_mail_field_from_template('email_cc')
            for mail_data in tools.email_split(email_cc):
                partners |= partners.find_or_create(mail_data)

        # Get partner_to
        if self.mail_template_id.partner_to:
            partner_to = self._get_mail_field_from_template('partner_to')
            partner_ids = self.mail_template_id._parse_partner_to(partner_to)
            partners |= self.env['res.partner'].sudo().browse(partner_ids).exists()

        return partners.filtered('email')

    def _get_task_attachments_data(self):
        """Get task attachments data for widget"""
        self.ensure_one()
        if not self.task_id:
            return []

        attachments = self.env['ir.attachment'].search([
            ('res_model', '=', 'project.task'),
            ('res_id', '=', self.task_id.id),
        ])

        return [
            {
                'id': attachment.id,
                'name': attachment.name,
                'mimetype': attachment.mimetype,
                'placeholder': False,
                'protect_from_deletion': True,
            }
            for attachment in attachments
        ]

    def _get_mail_template_attachments_data(self):
        """Get template attachments data for widget"""
        self.ensure_one()
        if not self.mail_template_id:
            return []

        return [
            {
                'id': attachment.id,
                'name': attachment.name,
                'mimetype': attachment.mimetype,
                'placeholder': False,
                'mail_template_id': self.mail_template_id.id,
                'protect_from_deletion': True,
            }
            for attachment in self.mail_template_id.attachment_ids
        ]

    # -------------------------------------------------------------------------
    # BUSINESS ACTIONS
    # -------------------------------------------------------------------------

    def action_send_email(self):
        """Send SERP report email"""
        self.ensure_one()

        if not self.mail_partner_ids:
            raise UserError(_('Please add at least one recipient'))

        if not self.partner_id.email:
            raise UserError(_('Partner has no email address'))

        # Prepare attachments from widget
        mail_attachments_widget = self.mail_attachments_widget or []
        seen_attachment_ids = set()
        to_exclude = {x['name'] for x in mail_attachments_widget if x.get('skip')}

        for attachment_data in mail_attachments_widget:
            if attachment_data['name'] in to_exclude and not attachment_data.get('manual'):
                continue

            try:
                attachment_id = int(attachment_data['id'])
            except ValueError:
                continue

            seen_attachment_ids.add(attachment_id)

        # Get actual attachments
        attachments = [
            (attachment.name, attachment.raw or attachment.datas)
            for attachment in self.env['ir.attachment'].browse(list(seen_attachment_ids)).exists()
        ]

        # Send email
        self.task_id.with_context(
            no_document=True,
            mail_notify_author=self.env.user.partner_id in self.mail_partner_ids,
        ).message_post(
            subject=self.mail_subject,
            body=self.mail_body,
            partner_ids=self.mail_partner_ids.ids,
            attachments=attachments,
            message_type='comment',
            subtype_xmlid='mail.mt_comment',
            # email_layout_xmlid='mail.mail_notification_layout_with_responsible_signature',
            # auto_delete=self.mail_template_id.auto_delete if self.mail_template_id else False,
            # mail_server_id=self.mail_template_id.mail_server_id.id if self.mail_template_id else False,

            **{  # noqa: PIE804
                'email_layout_xmlid': 'mail.mail_notification_layout_with_responsible_signature',
                'email_add_signature': not self.mail_template_id,
                'mail_auto_delete': self.mail_template_id.auto_delete,
                'mail_server_id': self.mail_template_id.mail_server_id.id,
                'reply_to_force_new': False,
            }
        )

        return {'type': 'ir.actions.act_window_close'}