from urllib import request
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import requests
import logging
import json
import base64
import urllib.request

_logger = logging.getLogger(__name__)


class ElkSms(models.Model):
    _inherit = "sms.sms"

    url = fields.Char('https://api.46elks.com/a1/sms')
    elk_sms_id = fields.Text(string="ELK SMS ID")
    elk_sms_status = fields.Selection([
        ('created', 'Created'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('delivered', 'Delivered')
    ])
    rec_model = fields.Char(string="Model Rec", readonly=True)
    rec_id = fields.Char(string="Rec ID", readonly=True)

    def send(self, delete_all=False, auto_commit=False, raise_exception=False):
        try:
            username, password = (self.env['ir.config_parameter'].get_param('elk_sms_auth')).split(',')
        except Exception as e:
            raise UserError(
                _('Error. Create a system parameter called "elk_sms_auth" containing the auth info like this: '
                  'username,password'))

        try:
            dryrun_toggle = (self.env['ir.config_parameter'].get_param('elk_sms_dryrun')).split(',')
        except Exception as e:
            raise UserError(
                _('Error. Create a system parameter called "elk_sms_dryrun" containing a yes or no depending on if '
                  'you want to send actual text messages or not. '))

        if username and password:
            response = requests.post(
                'https://api.46elks.com/a1/sms',
                auth=(username, password),
                data={'dryrun': dryrun_toggle, 'from': 'Reboot',
                      'to': self.convert_number(self.number), 'message': self.body,
                      'whendelivered': f"{self.env['ir.config_parameter'].get_param('web.base.url')}/sms"})
            _logger.warning(response.text)
            if response.status_code == 200:
                response = json.loads(response.content.decode("utf-8"))
                self.write({
                    'elk_sms_id': response.get('id', False),
                    'elk_sms_status': response.get('status', False),
                })
                self.state = "outgoing"
            else:
                response = response.content.decode("utf-8")
                raise ValidationError(_(response))

    def convert_number(self, number):
        if number and number[0] == '0':
            return f"{'+46'}{number[1::]}"
        elif number and number[0] == '+':
            return number
