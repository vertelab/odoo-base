# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution, third party addon
#    Copyright (C) 2004-2020 Vertel AB (<http://vertel.se>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api, _


import stomp
import ssl
import sys
import xmltodict


def parse_message(message):
    xml = None
    try:
        xml = xmltodict.parse(message, dict_constructor=dict)

        if (
            not isinstance(xml, dict)
            or not "msg" in xml.keys()
            or not isinstance(xml["msg"], dict)
            or not "key" in xml["msg"].keys()
            or not "data" in xml["msg"].keys()
        ):
            print("Incorrect XML format: %s" % message)
    except:
        # log parse error
        # ex = sys.exc_info()
        # print("Oops! %s occurred: %s" % (ex[0], ex[1]))
        print("Illegal XML format: '%s'" % message)

    return xml



import logging
_logger = logging.getLogger(__name__)




class MyListener(stomp.ConnectionListener):
    def on_error(self, frame):
        pass
        # ~ print('received an error "%s"' % frame.body)
    def on_message(self, frame):
        pass
        # ~ print('received a message "%s"' % frame.body)


class ResPartner(models.Model):
    _inherit = "res.partner"  

    @api.model
    def mq_listener(self): 
        host_port = (self.env['ir.config_parameter'].get_param('partner_mq_ipf.mqhost', '172.16.36.27'), self.env['ir.config_parameter'].get_param('partner_mq_ipf.mqport', '61613'))
        target = self.env['ir.config_parameter'].get_param('partner_mq_ipf.mqtarget', '/queue/Consumer.crm.VirtualTopic.arbetssokande.andring')
        mqconn = stomp.Connection10([host_port])
        
        if self.env['ir.config_parameter'].get_param('partner_mq_ipf.mqusessl', '1') == '1':
            mqconn.set_ssl(for_hosts=[host_port], ssl_version=ssl.PROTOCOL_TLS)

        mqconn.set_listener('', MyListener())

        mqconn.connect(
                    self.env['ir.config_parameter'].get_param('partner_mq_ipf.mquser', 'crm'),
                    self.env['ir.config_parameter'].get_param('partner_mq_ipf.mqpwd', 'hemligt'),
                    wait=True)
        # ~ conn = stomp.Connection()
        mqconn.subscribe(destination=target, id=1, ack='auto')
        # ~ mqconn.disconnect()


        # ~ try:
            # ~ while self.__keepgoing:
                # ~ time.sleep(1)
        # ~ finally:
            # ~ self.__conn.unsubscribe(self.__target)
            # ~ time.sleep(1)
            # ~ self.__conn.disconnect()
            # ~ self.debug_print("Stopped")
        





        # ~ self.env['ir.config_parameter'].get_param('partner_mq_ipf.mqdbglevel', '0')


