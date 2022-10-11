from urllib import request
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import requests
import logging
import json
import base64
import urllib.request

_logger = logging.getLogger(__name__)


class ElkSms(models.Model):
    _inherit = "sms.sms"

    url = fields.Char('https://api.46elks.com/a1/sms')

    def send(self, delete_all=False, auto_commit=False, raise_exception=False):
        if not self.body:
           _logger.warning(f"Unable to send sms: Missing Message {self=}")
           self.state  = "error"
           self.error_code = "sms_number_missing"
           return False
        if not self.number:
           _logger.warning(f"Unable to send sms: Missing Number {self=}")
           self.state  = "error"
           self.error_code = "sms_server" 
           return False
        try:
            auth_info = (self.env['ir.config_parameter'].get_param('elk_sms_auth')).split(',')
        except:
            raise UserError(
                _('Error. Create a system parameter called "elk_sms_auth" containing the auth info like this: '
                  'username,password'))

        try:
            dryrun_toggle = (self.env['ir.config_parameter'].get_param('elk_sms_dryrun')).split(',')
        except:
            raise UserError(
                _('Error. Create a system parameter called "elk_sms_dryrun" containing a yes or no depending on if '
                  'you want to send actual text messages or not. '))

        if auth_info:
            response = requests.post('https://api.46elks.com/a1/sms', auth=(auth_info[0], auth_info[1]),
                                     data={'dryrun': dryrun_toggle, 'from': 'Reboot', 'to': self.convert_number(self.number),'message': self.body,'whendelivered': f"{self.env['ir.config_parameter'].get_param('web.base.url')}/sms"})
            if 'Unexpected 0' in response.content.decode('utf-8'):
                #raise UserError(_('Error. Input a +46.... number instead of 0...'))
                _logger.warning(_('Error. Input a +46.... number instead of 0...'))
                self.state  = "error"
                return False
            if 'requires Basic' in response.content.decode('utf-8'):
                #raise UserError(_('Error. Check if the auth info in the system parameter "elk_sms_auth" is valid.'))
                _logger.warning(_('Error. Check if the auth info in the system parameter "elk_sms_auth" is valid.'))
                self.state  = "error"
                return False
            if 'Not enough credits' in response.content.decode('utf-8'):
                #raise UserError(_('Error. Not enough money to send message, add funds.'))
                _logger.warning(_('Error. Not enough money to send message, add funds.'))
                self.state  = "error"
                return False
            if 'Missing key to' in response.content.decode('utf-8'):
                #raise UserError(_('Error. Missing key to (i have no idea to what, probably weird phone number.)'))
                _logger.warning(_('Error. Missing key to (i have no idea to what, probably weird phone number.)'))
                self.state  = "error"
                return False
            self.state  = "sent"
            return response

    def convert_number(self, number):
        if number and number[0] == '0':
            return f"{'+46'}{number[1::]}"
        elif number and number[0] == '+':
            return number
