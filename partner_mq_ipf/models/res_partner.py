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

import json
import logging
import stomp
import ssl
import sys
import time
import xmltodict

_logger = logging.getLogger(__name__)

def connect_and_subscribe(mqconn, user, pwd, target, clientid=4):
    mqconn.connect(user, pwd, wait=True)
    mqconn.subscribe(destination=target, clientid=4, ack="client")

PREN="prenumerera-arbetssokande"
PNR="personnummer"
PREVPNR="tidigarePersonnummer"
SID="sokandeId"
MSGTYPE="meddelandetyp"
TIMESTAMP="tidpunkt"

class AsokResPartnerListener(stomp.ConnectionListener):
    __env = None
    __conn = None
    __user = None 
    __pwd = None
    __target = None
    __msglist = list()
    __clientid = None

    def __init__(self, env, mqconn, user, pwd, target, clientid=4):
        self.__env = env
        self.__conn = mqconn
        self.__user = user
        self.__pwd = pwd
        self.__target = target
        self.__clientid = clientid

    def __parse_message(self, message):
        xmldict = None
        try:
            xmldict = xmltodict.parse(message, dict_constructor=dict)
            # Validate xml dict

            if (
                not isinstance(xmldict, dict)
                or not PREN in xmldict.keys()
                or not isinstance(xmldict[PREN], dict)
                or not PNR in xmldict[PREN].keys()
                or not SID in xmldict[PREN].keys()
                or not MSGTYPE in xmldict[PREN].keys()
            ):
                xmldict = None
                raise ValueError("Illegal XMLFormat")
        except:
            # log parse error
            # ex = sys.exc_info()
            # print("Oops! %s occurred: %s" % (ex[0], ex[1]))
            _logger.warning("Illegal XML format: '%s'" % message)
            return None

        return xmldict[PREN]

    def _handle_message(self, message):
        data = self.__parse_message(message)

        if data:
            # Add message to list
            self.__msglist.append(data)

    def get_list(self):
        return self.__msglist

    def clear_list(self):
        self.__msglist = list()

    def on_error(self, headers, body):
        """
        Called by the STOMP connection when an ERROR frame is received.

        :param dict headers: a dictionary containing all headers sent by the server as key/value pairs.
        :param body: the frame's payload - usually a detailed error description.
        """
        _logger.error("Asok MQ Listener error: %s - %s" % (headers, body))
 
    def on_message(self, headers, msg):
        _logger.debug("Asok MQ Listener on_message: {0} - {1}".format(headers, msg))
        self._handle_message(msg)
        # tell MQ we handled the message
        self.__conn.ack(headers["message-id"])
    
    def on_disconnected(self):
        _logger.warning('Asok MQ Listener disconnected from MQ - Tring to reconnect')
        connect_and_subscribe(self.__conn, self.__user, self.__pwd, self.__target, self.__clientid)

    def on_connecting(self, host_and_port):
        """
        Called by the STOMP connection once a TCP/IP connection to the
        STOMP server has been established or re-established. Note that
        at this point, no connection has been established on the STOMP
        protocol level. For this, you need to invoke the "connect"
        method on the connection.

        :param (str,int) host_and_port: a tuple containing the host name and port number to which the connection
            has been established.
        """
        _logger.debug("Asok MQ Listener on_conecting: {0}".format(host_and_port))

    def on_connected(self, headers, body):
        """
        Called by the STOMP connection when a CONNECTED frame is
        received (after a connection has been established or
        re-established).

        :param dict headers: a dictionary containing all headers sent by the server as key/value pairs.
        :param body: the frame's payload. This is usually empty for CONNECTED frames.
        """
        _logger.debug("Asok MQ Listener on_connected: %s - %s" % (headers, body))

class STOMResPartnerListener(stomp.ConnectionListener):
    __env = None
    __conn = None
    __user = None 
    __pwd = None
    __target = None
    __clientid = None
    __msglist = list()

    def __init__(self, env, mqconn, user, pwd, target, clientid=4):
        self.__env = env
        self.__conn = mqconn
        self.__user = user
        self.__pwd = pwd
        self.__target = target
        self.__clientid = clientid

    def __parse_message(self, message):
        try:
            # Assume JSON
            stom_list = json.loads(message)
            # Assume list of dicts or get exception
            return list(filter(lambda s: s["stom_track"] == 1, stom_list))
        except:
            _logger.warning("Invalid JSON format %s" % message)
            return None

    def _handle_message(self, message):
        stomlist = self.__parse_message(message)

        if stomlist and len(stomlist) > 0:
            # Call the method
            _logger.debug("STOM MQ Listener adding to list, %s " % len(stomlist))
            self.__msglist.append(stomlist)
        else:
            _logger.debug("STOM MQ Listener nothing found")

    def get_list(self):
        return self.__msglist

    def clear_list(self):
        self.__msglist = list()

    def on_error(self, headers, body):
        """
        Called by the STOMP connection when an ERROR frame is received.

        :param dict headers: a dictionary containing all headers sent by the server as key/value pairs.
        :param body: the frame's payload - usually a detailed error description.
        """
        _logger.error("STOM MQ Listener error: %s - %s" % (headers, body))
 
    def on_message(self, headers, msg):
        _logger.debug("STOM MQ Listener on_message: {0} - {1}".format(headers, msg))
        self._handle_message(msg)
        # tell MQ we handled the message
        self.__conn.ack(headers["message-id"])
    
    def on_disconnected(self):
        _logger.warning('STOM MQ Listener disconnected from MQ - Tring to reconnect')
        connect_and_subscribe(self.__conn, self.__user, self.__pwd, self.__target, self.__clientid)

    def on_connecting(self, host_and_port):
        """
        Called by the STOMP connection once a TCP/IP connection to the
        STOMP server has been established or re-established. Note that
        at this point, no connection has been established on the STOMP
        protocol level. For this, you need to invoke the "connect"
        method on the connection.

        :param (str,int) host_and_port: a tuple containing the host name and port number to which the connection
            has been established.
        """
        _logger.debug("STOM MQ Listener on_conecting: {0}".format(host_and_port))

    def on_connected(self, headers, body):
        """
        Called by the STOMP connection when a CONNECTED frame is
        received (after a connection has been established or
        re-established).

        :param dict headers: a dictionary containing all headers sent by the server as key/value pairs.
        :param body: the frame's payload. This is usually empty for CONNECTED frames.
        """
        _logger.debug("STOM MQ Listener on_connected: %s - %s" % (headers, body))

class ResPartner(models.Model):
    _inherit = "res.partner"  

    def __get_host_port(self):
        str = self.env['ir.config_parameter'].get_param('partner_mq_ipf.mqhostport', '172.16.36.27:61613')
        hosts = list()
        for vals in str.split(','):
            hosts.append(tuple(vals.split(':')))

        return hosts

    @api.model
    def mq_asok_listener(self, minutes_to_live = 10): 
        _logger.info("Asok MQ Listener started.")
        host_port = self.__get_host_port()
        target = self.env['ir.config_parameter'].get_param('partner_mq_ipf.target_asok', '/topic/Consumer.crm.VirtualTopic.arbetssokande.andring')
        usr = self.env['ir.config_parameter'].get_param('partner_mq_ipf.mquser', 'crm')
        pwd = self.env['ir.config_parameter'].get_param('partner_mq_ipf.mqpwd', 'topsecret')

        mqconn = stomp.Connection10(host_port)
        
        if self.env['ir.config_parameter'].get_param('partner_mq_ipf.mqusessl', '1') == '1':
            mqconn.set_ssl(for_hosts=host_port, ssl_version=ssl.PROTOCOL_TLS)
            _logger.debug("Asok MQ Listener - Using TLS")
        else:
            _logger.debug("Asok MQ Listener - Not using TLS")

        
        respartnerlsnr = AsokResPartnerListener(self.env, mqconn, usr, pwd, target, 4)
        mqconn.set_listener('', respartnerlsnr)
        
        try:
            connect_and_subscribe(
                mqconn,
                usr,
                pwd,
                target
            )

            counter = 12 * minutes_to_live # Number of 5 sek slices to wait
            while counter > 0:
                time.sleep(5) # wait for a bit
                mqconn.unsubscribe(target)
                # handle list of messages
                for msg in respartnerlsnr.get_list():
                    customer_id = msg.get(SID)
                    social_security_number = msg.get(PNR)
                    former_social_security_number = msg.get(PREVPNR, None)
                    message_type = msg.get(MSGTYPE) 
                    _logger.info("Asok MQ Listener - calling rask_controller")
                    _logger.debug("Asok MQ Listener - rask_controller: %s" % msg)
                    self.env['res.partner'].rask_controller(customer_id, social_security_number, former_social_security_number, message_type)

                self.env.cr.commit()
                respartnerlsnr.clear_list()
                cronstop = self.env['ir.config_parameter'].get_param('partner_mq_ipf.cronstop', '0')

                if cronstop == '0':
                    mqconn.subscribe(target)
                    counter -= 1
                else:
                    counter = 0
                
        finally:
            
            time.sleep(1)
            if mqconn.is_connected():
                mqconn.disconnect()

    def mq_stom_listener(self, minutes_to_live = 10): 
        _logger.info("STOM MQ Listener started.")
        host_port = self.__get_host_port()
        target = self.env['ir.config_parameter'].get_param('partner_mq_ipf.target_STOM', '/topic/Consumer.crm.VirtualTopic.arbetssokande.andring')
        usr = self.env['ir.config_parameter'].get_param('partner_mq_ipf.mquser', 'crm')
        pwd = self.env['ir.config_parameter'].get_param('partner_mq_ipf.mqpwd', 'topsecret')

        _logger.debug("STOM MQ Listener patameters - %s %s - %s %s" % ([host_port], target, usr, pwd))

        mqconn = stomp.Connection10(host_port)
        
        if self.env['ir.config_parameter'].get_param('partner_mq_ipf.mqusessl', '1') == '1':
            mqconn.set_ssl(for_hosts=host_port, ssl_version=ssl.PROTOCOL_TLS)
            _logger.debug("STOM MQ Listener - Using TLS")
        else:
            _logger.debug("STOM MQ Listener - Not using TLS")

        respartnerlsnr = STOMResPartnerListener(self.env, mqconn,usr,pwd,target,4)
        mqconn.set_listener('', respartnerlsnr)
        

        try:
            connect_and_subscribe(
                mqconn,
                usr,
                pwd,
                target
            )
            counter = 12 * minutes_to_live # Number of 5 sek slices to wait
            while counter > 0:
                time.sleep(5) # wait for a bit
                mqconn.unsubscribe(target)

                # handle list of messages
                for msg in respartnerlsnr.get_list():
                    _logger.info("STOM MQ Listener - calling send_to_stom_track")
                    _logger.debug("STOM MQ Listener - send_to_stom_track: %s" % msg)
                    self.env['res.partner'].send_to_stom_track(msg)

                self.env.cr.commit()
                respartnerlsnr.clear_list()
                cronstop = self.env['ir.config_parameter'].get_param('partner_mq_ipf.cronstop', '0')

                if cronstop == '0':
                    mqconn.subscribe(target)
                    counter -= 1
                else:
                    counter = 0

        finally:
            
            time.sleep(1)
            if mqconn.is_connected():
                mqconn.disconnect()

