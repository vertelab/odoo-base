# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools import html2plaintext


class MailComposeMessage(models.TransientModel):
    _inherit = "mail.compose.message"

    include_thread = fields.Boolean(
        string="Include Thread",
        help="Append the previous message thread to the outgoing email body.",
    )

    def get_mail_values(self, res_ids):
        results = super().get_mail_values(res_ids)

        if not self.include_thread:
            return results

        for res_id in res_ids:
            mail_values = results.get(res_id)
            if not mail_values:
                continue

            thread_html = self._build_thread_html(res_id)

            if not thread_html:
                continue

            # body_html is used by mass_mail mode; body is used by message_post mode
            for body_key in ('body_html', 'body'):
                if body_key in mail_values and mail_values[body_key]:
                    mail_values[body_key] = mail_values[body_key] + thread_html
                elif body_key in mail_values:
                    mail_values[body_key] = thread_html

        return results

    def _build_thread_html(self, res_id):
        """Build an HTML block of previous messages for the given record.

        Only includes messages of type 'comment' or 'email' that are not
        internal notes, ordered from oldest to newest, excluding the
        current wizard body to avoid duplication.

        :param int res_id: ID of the related document record.
        :returns str: HTML string of the thread, or empty string if none found.
        """
        if not self.model or not res_id:
            return ""

        domain = [
            ("model", "=", self.model),
            ("res_id", "=", res_id),
            ("message_type", "in", ("comment", "email")),
            ("is_internal", "=", False),
            ("subtype_id.internal", "=", False),
        ]

        # Exclude the message being composed right now
        if self.parent_id:
            domain.append(("id", "<", self.parent_id.id))

        messages = self.env["mail.message"].search(domain, order="id asc")

        if not messages:
            return ""

        parts = [
            """
            <div style="margin-top:20px; padding-top:16px;
                        border-top:1px solid #d0d0d0; color:#555;
                        font-family:Arial, sans-serif; font-size:12px;">
                <p style="margin:0 0 12px 0; font-weight:bold; color:#333;">
                    — Previous messages —
                </p>
            """
        ]

        for msg in messages:
            author = msg.author_id.name if msg.author_id else (msg.email_from or _("Unknown"))
            date_str = msg.date.strftime("%d %b %Y %H:%M") if msg.date else ""
            subject = msg.subject or ""
            body = msg.body or ""

            parts.append(
                f"""
                <div style="margin-bottom:14px; padding:10px 12px;
                            background:#f9f9f9; border-left:3px solid #aaa;
                            border-radius:2px;">
                    <p style="margin:0 0 4px 0; font-size:11px; color:#888;">
                        <strong style="color:#333;">{author}</strong>
                        &nbsp;·&nbsp; {date_str}
                        {"&nbsp;·&nbsp; <em>" + subject + "</em>" if subject else ""}
                    </p>
                    <div style="margin-top:6px; color:#444; font-size:12px;">
                        {body}
                    </div>
                </div>
                """
            )

        parts.append("</div>")
        return "".join(parts)
