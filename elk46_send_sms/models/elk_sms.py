from urllib import request
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import requests
import logging
import json
import base64
import urllib.request

_logger = logging.getLogger("------dmitri-------")

class ElkSms(models.Model):
    _inherit = "sms.sms"

    url = fields.Char('https://api.46elks.com/a1/sms')

    #46739299019
    #auth=('a6ba22729971395309fd3a973ee352f93', 'AFE26B724029E6B79CFFAAD9C9762545')
    def send(self, number=False, body=False, delete_all=False, auto_commit=False, raise_exception=False):
        auth_info = (self.env['ir.config_parameter'].get_param('elk_sms_auth')).split(',')

        def read_json_from_site(response):
            url = 'https://api.46elks.com/a1/sms'
            request = urllib.request.Request(url)
            string = '%s:%s' % (auth_info[0], auth_info[1])
            base64string = base64.standard_b64encode(string.encode('utf-8'))
            request.add_header('Authorization', 'Basic %s' % base64string.decode('utf-8'))
            result = urllib.request.urlopen(request)
            result_json = json.loads(result.read())

            for line in result_json['data']:
                if line['id'] == json.loads(response.content.decode('utf-8'))['id']:
                    _logger.warning(line['status'])
                    if line['status'] == 'delivered':

                        return True
            raise UserError(_('Error. Did you input the correct number?'))
        
        if auth_info:
            response = requests.post('https://api.46elks.com/a1/sms',   auth=(auth_info[0], auth_info[1]),
                                     data={'dryrun': 'no', 'from': 'Reboot', 'to': self.convert_number(number), 'message': body,
                                     'whendelivered': 'moe.vertel.se:1014/sms?db'})
            
            if read_json_from_site(response):
                if 'Unexpected 0' in response.content.decode('utf-8'):
                    raise UserError(_('Input a +46.... number instead of 0...'))

                return response
        else:
            raise UserError(_('No system parameter containing the mobile authentification token'))

    def convert_number(self, number):
        number_out = 0
        if number[0] == '0':
            number_out = f"{'+46'}{number[1::]}"
        return number_out

    
