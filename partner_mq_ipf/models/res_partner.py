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

from odoo import models, fields, api, _, registry

import json
import logging
import stomp
import ssl
import sys
import time
import xmltodict
import threading

_logger = logging.getLogger(__name__)


def subscribe(mqconn, target, clientid=4):
    mqconn.subscribe(destination=target, clientid=clientid, ack="client")


def connect_and_subscribe(mqconn, user, pwd, target, clientid=4):
    mqconn.connect(user, pwd, wait=True)
    subscribe(mqconn, target, clientid=clientid)


PREN = "prenumerera-arbetssokande"
PNR = "personnummer"
PREVPNR = "tidigarePersonnummer"
SID = "sokandeId"
MSGTYPE = "meddelandetyp"
TIMESTAMP = "tidpunkt"


class AsokResPartnerListener(stomp.ConnectionListener):
    def __init__(self, mqconn, user, pwd, target, clientid=4):
        self.__conn = mqconn
        self.__user = user
        self.__pwd = pwd
        self.__target = target
        self.__clientid = clientid
        self.__msglist = list()

    def __parse_message(self, message):
        xmldict = None
        try:
            xmldict = xmltodict.parse(message, dict_constructor=dict)
            # Validate xml dict
            _logger.debug("__parse_message: %s" % xmldict)
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

    def _handle_message(self, headers, message):
        data = self.__parse_message(message)
        _logger.debug("_handle_message: %s" % data)
        if data:
            # Add message to list
            self.__msglist.append((headers, data))

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
        self._handle_message(headers, msg)

    def ack_message(self, msg):
        headers, body = msg
        # tell MQ we handled the message
        self.__conn.ack(headers["message-id"])

    def on_disconnected(self):
        # Probably happened because we asked to disconnect
        _logger.warning(
            "Asok MQ Listener disconnected from MQ - NOT Trying to reconnect"
        )

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
    __conn = None
    __user = None
    __pwd = None
    __target = None
    __clientid = None

    def __init__(self, mqconn, user, pwd, target, clientid=4):
        self.__conn = mqconn
        self.__user = user
        self.__pwd = pwd
        self.__target = target
        self.__clientid = clientid
        self.__msglist = list()

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
        # TODO: Should probably move ack to successful message handling. See AsokResPartnerListener
        self.__conn.ack(headers["message-id"])

    def on_disconnected(self):
        # Probably happened because we asked to disconnect
        _logger.warning("STOM MQ Listener disconnected from MQ - Tring to reconnect")

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
        str = self.env["ir.config_parameter"].get_param(
            "partner_mq_ipf.mqhostport", "172.16.36.27:61613"
        )
        hosts = list()
        for vals in str.split(","):
            hosts.append(tuple(vals.split(":")))

        return hosts

    @api.model
    def mq_asok_sender(self, msg_list, ack_list, do_list, lock):
        """Method run in a seperate thread. Sends requests to RASK."""
        new_cr = registry(self.env.cr.dbname).cursor()
        uid, context = self.env.uid, self.env.context
        with api.Environment.manage():
            env_new = api.Environment(new_cr, uid, context)
            # passing a bool in do_list to indicate if we should keep
            # running this loop. What is a better solution?
            while do_list[0]:
                message = False
                if msg_list:
                    try:
                        with lock:
                            message = msg_list.pop()
                        if message:
                            _logger.debug("Asok MQ Sender: sending request to RASK")
                            headers, msg = message
                            customer_id = msg.get(SID)
                            social_security_number = msg.get(PNR)
                            former_social_security_number = msg.get(PREVPNR, None)
                            message_type = msg.get(MSGTYPE)
                            # Send request to RASK
                            env_new["res.partner"].rask_controller(
                                customer_id,
                                social_security_number,
                                former_social_security_number,
                                message_type,
                            )
                            # append message to ack_list to let main
                            # thread know that this can be ACK'd
                            with lock:
                                ack_list.append(message)
                        message = False
                    except:
                        _logger.exception(
                            "Asok MQ Sender: error sending request to RASK!"
                        )
                else:
                    # slow down so we don't loop all the time
                    time.sleep(1)
        # close our new cursor
        env_new.cr.close()

    @api.model
    def mq_asok_listener(self, minutes_to_live=10):
        _logger.info("Asok MQ Listener started.")
        host_port = self.__get_host_port()
        target = self.env["ir.config_parameter"].get_param(
            "partner_mq_ipf.target_asok",
            "/topic/Consumer.crm.VirtualTopic.arbetssokande.andring",
        )
        usr = self.env["ir.config_parameter"].get_param("partner_mq_ipf.mquser", "crm")
        pwd = self.env["ir.config_parameter"].get_param(
            "partner_mq_ipf.mqpwd", "topsecret"
        )
        stomp_log_level = self.env["ir.config_parameter"].get_param(
            "partner_mq_ipf.stomp_logger", "INFO"
        )

        # decide the stomper log level depending on param
        stomp_logger = logging.getLogger("stomp.py")
        stomp_logger.setLevel(getattr(logging, stomp_log_level))

        mqconn = stomp.Connection10(host_port)

        if (
            self.env["ir.config_parameter"].get_param("partner_mq_ipf.mqusessl", "1")
            == "1"
        ):
            mqconn.set_ssl(for_hosts=host_port, ssl_version=ssl.PROTOCOL_TLS)
            _logger.debug("Asok MQ Listener - Using TLS")
        else:
            _logger.debug("Asok MQ Listener - Not using TLS")

        respartnerlsnr = AsokResPartnerListener(mqconn, usr, pwd, target, 4)
        mqconn.set_listener("", respartnerlsnr)

        try:
            connect_and_subscribe(mqconn, usr, pwd, target)

            counter = 12 * minutes_to_live  # Number of 5 sek slices to wait
            # define common lists to be used between threads
            msg_list = []
            ack_list = []
            # passing a bool in do_list to indicate if we should keep
            # running mq_asok_sender. What is a better solution?
            do_list = [True]
            # define a lock so we can lock msg_list while updating it
            # in each thread.
            lock = threading.Lock()
            # create a new thread running mq_asok_sender function
            sender_thread = threading.Thread(
                target=self.mq_asok_sender, args=(msg_list, ack_list, do_list, lock)
            )
            sender_thread.start()

            processed_list = []
            # run loop
            while counter > 0:
                # Let messages accumulate
                time.sleep(5)
                _logger.debug(
                    "__msglist before unsubscribe: %s" % respartnerlsnr.get_list()
                )
                # check if we have ACKs to send out
                with lock:
                    while len(ack_list) > 0:
                        try:
                            # read ack_list and send ACK to MQ queue
                            ack_message = ack_list.pop()
                            # use a generator to find the matching 
                            # message from current list not sure if this 
                            # is actually needed but I've implemented it
                            # to stop problems with us ACKing messages 
                            # that disapear...
                            ack_message_current = next(
                                (
                                    msg
                                    for msg in respartnerlsnr.get_list()
                                    if msg[0]["message-id"]
                                    == ack_message[0]["message-id"]
                                ),
                                False,
                            )
                            if not ack_message_current:
                                # this message ghosted us????
                                _logger.warn(
                                    "Asok MQ Listener - COULD NOT FIND MESSAGE TO ACC: %s"
                                    % ack_message[0]["message-id"]
                                )
                            else:
                                _logger.debug(
                                    "Asok MQ Listener - ACK: %s"
                                    % ack_message_current[0]["message-id"]
                                )
                                respartnerlsnr.ack_message(ack_message_current)
                            ack_message_current = False
                            ack_message = False
                        except:
                            _logger.exception("Asok MQ Listener: error ACK")
                # Stop listening
                mqconn.unsubscribe(target)

                # Handle list of messages
                for message in respartnerlsnr.get_list():
                    _logger.debug("Asok MQ Listener - adding message to internal queue")
                    if message[0]["message-id"] not in processed_list:
                        try:
                            with lock:
                                msg_list.append(message)
                            # append message to processed_list to keep
                            # track of what messages have been processed
                            # this is needed since we will recieve already
                            # processed messages until they are ACK'd
                            processed_list.append(message[0]["message-id"])
                        except:
                            _logger.exception(
                                "Asok MQ Listener: error adding message to internal queue"
                            )
                message = False
                self.env.cr.commit()
                # Clear accumulated messages
                respartnerlsnr.clear_list()
                # Check if stop has been called
                cronstop = self.env["ir.config_parameter"].get_param(
                    "partner_mq_ipf.cronstop", "0"
                )
                if cronstop == "0":
                    counter -= 1
                    if counter > 0:
                        # Only subscribe if we haven't reached the end yet
                        subscribe(mqconn, target)
                else:
                    counter = 0
        except:
            _logger.exception("Something went wrong in MQ")
        finally:
            # send signal to stop other thread
            do_list[0] = False
            time.sleep(1)
            if mqconn.is_connected():
                mqconn.disconnect()

    def mq_stom_listener(self, minutes_to_live=10):
        _logger.info("STOM MQ Listener started.")
        host_port = self.__get_host_port()
        target = self.env["ir.config_parameter"].get_param(
            "partner_mq_ipf.target_STOM",
            "/topic/Consumer.crm.VirtualTopic.arbetssokande.andring",
        )
        usr = self.env["ir.config_parameter"].get_param("partner_mq_ipf.mquser", "crm")
        pwd = self.env["ir.config_parameter"].get_param(
            "partner_mq_ipf.mqpwd", "topsecret"
        )
        stomp_log_level = self.env["ir.config_parameter"].get_param(
            "partner_mq_ipf.stomp_logger", "INFO"
        )

        # decide the stomper log level depending on param
        stomp_logger = logging.getLogger("stomp.py")
        stomp_logger.setLevel(getattr(logging, stomp_log_level))

        _logger.debug(
            "STOM MQ Listener patameters - %s %s - %s %s"
            % ([host_port], target, usr, pwd)
        )

        mqconn = stomp.Connection10(host_port)

        if (
            self.env["ir.config_parameter"].get_param("partner_mq_ipf.mqusessl", "1")
            == "1"
        ):
            mqconn.set_ssl(for_hosts=host_port, ssl_version=ssl.PROTOCOL_TLS)
            _logger.debug("STOM MQ Listener - Using TLS")
        else:
            _logger.debug("STOM MQ Listener - Not using TLS")

        respartnerlsnr = STOMResPartnerListener(mqconn, usr, pwd, target, 4)
        mqconn.set_listener("", respartnerlsnr)

        try:
            connect_and_subscribe(mqconn, usr, pwd, target)
            counter = 12 * minutes_to_live  # Number of 5 sek slices to wait
            while counter > 0:
                time.sleep(5)  # wait for a bit
                mqconn.unsubscribe(target)

                # handle list of messages
                for msg in respartnerlsnr.get_list():
                    _logger.info("STOM MQ Listener - calling send_to_stom_track")
                    _logger.debug("STOM MQ Listener - send_to_stom_track: %s" % msg)
                    self.env["res.partner"].send_to_stom_track(msg)

                self.env.cr.commit()
                respartnerlsnr.clear_list()
                cronstop = self.env["ir.config_parameter"].get_param(
                    "partner_mq_ipf.cronstop", "0"
                )

                if cronstop == "0":
                    mqconn.subscribe(target)
                    counter -= 1
                else:
                    counter = 0

        finally:

            time.sleep(1)
            if mqconn.is_connected():
                mqconn.disconnect()
