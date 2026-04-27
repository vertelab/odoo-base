# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import lxml.html

class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    include_thread = fields.Boolean(
        string="Include Thread",
        help="Append the previous message thread to the outgoing email body.",
    )

    def get_mail_values(self, res_ids):
        """ Generate mail values, separating clean body for DB and full body for email. """
        results = super(MailComposeMessage, self).get_mail_values(res_ids)

        if not self.include_thread:
            return results

        for res_id in res_ids:
            mail_values = results.get(res_id)
            if not mail_values:
                continue

            thread_html = self._build_thread_html(res_id)
            if not thread_html:
                continue

            # We keep 'body' clean for the database/chatter
            # We add 'full_body_with_thread' for our notification system to intercept
            clean_body = mail_values.get('body', '')
            mail_values['full_body_with_thread'] = clean_body + thread_html

            # For mass mailing (mail.mail), we want the full thread in body_html
            if self.composition_mode == 'mass_mail' and 'body_html' in mail_values:
                 mail_values['body_html'] = (mail_values.get('body_html') or '') + thread_html

        return results

    def _build_thread_html(self, res_id):
        """ Build an HTML block of previous messages, stripping nested threads. """
        if not self.model or not res_id:
            return ""

        domain = [
            ("model", "=", self.model),
            ("res_id", "=", res_id),
            ("message_type", "in", ("comment", "email")),
            ("is_internal", "=", False),
        ]

        if self.parent_id:
            domain.append(("id", "<=", self.parent_id.id))

        messages = self.env["mail.message"].search(domain, order="id desc", limit=10)
        if not messages:
            return ""
        messages = messages.sorted("id")

        parts = [
            """
            <div class="o_mail_thread_history" style="margin-top:20px; padding-top:16px;
                        border-top:1px solid #d0d0d0; color:#555;
                        font-family:Arial, sans-serif; font-size:12px;">
                <p style="margin:0 0 12px 0; font-weight:bold; color:#333;">
                    — Previous messages —
                </p>
            """
        ]

        for msg in messages:
            author = msg.author_id.name if msg.author_id else (msg.email_from or _("Unknown"))
            date_str = fields.Datetime.to_string(msg.date) if msg.date else ""
            body = msg.body or ""

            # Strip previous history from this message's body to avoid exponential duplication
            if 'o_mail_thread_history' in body:
                try:
                    root = lxml.html.fromstring(body)
                    for node in root.xpath('//*[contains(@class, "o_mail_thread_history")]'):
                        node.getparent().remove(node)
                    body = lxml.html.tostring(root, pretty_print=False, encoding='unicode')
                except Exception:
                    pass

            parts.append(
                f"""
                <div style="margin-bottom:14px; padding:10px 12px;
                            background:#f9f9f9; border-left:3px solid #aaa;
                            border-radius:2px;">
                    <p style="margin:0 0 4px 0; font-size:11px; color:#888;">
                        <strong style="color:#333;">{author}</strong>
                        &nbsp;·&nbsp; {date_str}
                    </p>
                    <div style="margin-top:6px; color:#444; font-size:12px;">
                        {body}
                    </div>
                </div>
                """
            )

        parts.append("</div>")
        return "".join(parts)
