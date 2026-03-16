# -*- coding: utf-8 -*-
from lxml import etree
import lxml.html
from odoo import models


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    def _message_parse_extract_payload_postprocess(self, message, payload_dict):
        result = super()._message_parse_extract_payload_postprocess(message, payload_dict)
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
