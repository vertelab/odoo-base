# -*- coding: utf-8 -*-
import lxml.html
from odoo import models, api

class MessageWrapper:
    """ Proxy for mail.message record to inject a custom body during rendering. """
    def __init__(self, message, body):
        self._message = message
        self._body = body

    def __getattr__(self, name):
        if name == 'body':
            return self._body
        return getattr(self._message, name)

    def __getitem__(self, key):
        if key == 'body':
            return self._body
        return self._message[key]
    
    @property
    def body(self):
        return self._body

    def __bool__(self):
        return bool(self._message)

    def __len__(self):
        return len(self._message)

class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    def _notify_thread(self, message, msg_vals=False, notify_by_email=True, **kwargs):
        """ Capture full_body_with_thread and ensure it's in msg_vals for email notification. """
        if kwargs.get('full_body_with_thread'):
            if not msg_vals:
                msg_vals = {}
            msg_vals['full_body_with_thread'] = kwargs.get('full_body_with_thread')
        return super(MailThread, self)._notify_thread(message, msg_vals=msg_vals, notify_by_email=notify_by_email, **kwargs)

    def _notify_prepare_template_context(self, message, msg_vals, model_description=False, mail_auto_delete=True):
        """ Override to inject the full thread body into the email template context. """
        res = super(MailThread, self)._notify_prepare_template_context(
            message, msg_vals, model_description=model_description, mail_auto_delete=mail_auto_delete
        )
        if msg_vals and msg_vals.get('full_body_with_thread'):
            # Swap the message in context with our wrapper that has the full body
            res['message'] = MessageWrapper(message, msg_vals['full_body_with_thread'])
        return res

    def _message_parse_extract_payload_postprocess(self, message, payload_dict):
        """ Strip thread history from incoming emails to keep chatter clean. """
        result = super(MailThread, self)._message_parse_extract_payload_postprocess(message, payload_dict)
        body = result.get('body', '')

        if body and 'o_mail_thread_history' in body:
            try:
                root = lxml.html.fromstring(body)
                for node in root.xpath('//*[contains(@class, "o_mail_thread_history")]'):
                    node.getparent().remove(node)
                result['body'] = lxml.html.tostring(root, pretty_print=False, encoding='unicode')
            except Exception:
                pass

        return result
