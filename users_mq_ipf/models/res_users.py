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
import threading

_logger = logging.getLogger(__name__)


def subscribe(mqconn, target, clientid=4):
    mqconn.subscribe(destination=target, clientid=clientid, ack="client")


def connect_and_subscribe(mqconn, user, pwd, target, clientid=4):
    _logger.info(f"user: {user} pwd: {pwd}")
    mqconn.connect(user, pwd, wait=True)
    subscribe(mqconn, target, clientid=clientid)

SIGN = "signatur"
CODE = "kontorskod"
SECTION = "sektion"
TYPE = "notifieringstyp"
ACCESS = "behorighet"
AISF_OFFICER_SYNC_PROCESS = "AIS-F OFFICER SYNC"
OFFICER_SYNC = "OFFICER SYNC"

class OfficerListener(stomp.ConnectionListener):
    def __init__(self, mqconn, user, pwd, target, clientid=4):
        self.__conn = mqconn
        self.__user = user
        self.__pwd = pwd
        self.__target = target
        self.__clientid = clientid
        self.__msglist = list()

    def __parse_message(self, message):
        msgdict = {}
        try:
            msgdict = json.loads(message)
        except:
            return None
        return msgdict

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
        _logger.error("Officer MQ Listener error: %s - %s" % (headers, body))

    def on_message(self, headers, msg):
        _logger.debug("Officer MQ Listener on_message: {0} - {1}".format(headers, msg))
        self._handle_message(headers, msg)

    def ack_message(self, msg):
        headers, body = msg
        # tell MQ we handled the message
        self.__conn.ack(headers["message-id"])

    def on_disconnected(self):
        # Probably happened because we asked to disconnect
        _logger.warning(
            "Officer MQ Listener disconnected from MQ - NOT Trying to reconnect"
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
        _logger.debug("Officer MQ Listener on_conecting: {0}".format(host_and_port))

    def on_connected(self, headers, body):
        """
        Called by the STOMP connection when a CONNECTED frame is
        received (after a connection has been established or
        re-established).

        :param dict headers: a dictionary containing all headers sent by the server as key/value pairs.
        :param body: the frame's payload. This is usually empty for CONNECTED frames.
        """
        _logger.debug("Officer MQ Listener on_connected: %s - %s" % (headers, body))


class ResUsers(models.Model):
    _inherit = "res.users"

    def __get_host_port(self):
        str = self.env["ir.config_parameter"].get_param(
            "users_mq_ipf.mqhostport", "ipfmq1-utv.arbetsformedlingen.se:61613"
        )
        hosts = list()
        for vals in str.split(","):
            hosts.append(tuple(vals.split(":")))

        return hosts

    @api.model
    def mq_officer_sender(self, msg_list, ack_list, do_list, lock):
        """Method run in a seperate thread. Sends requests."""

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
                            _logger.debug("Officer MQ Sender: finding user")
                            headers, msg = message
                            signature = msg.get(SIGN)
                            office_code = msg.get(CODE)
                            msg_type = msg.get(TYPE)
                            access = msg.get(ACCESS)
                            eventid = headers["message-id"]
                            _logger.debug(f"Got message with  {signature}, "
                                          f"office code {office_code}, "
                                          f"type {msg_type}, "
                                          f"access {access}")
                            # not sure how specific the search has to be to find the right object
                            user_id = self.env['res.users'].search([('login', '=', signature)])
                            office_id = self.env['hr.department'].search([('office_code', '=', office_code)])
                            if not user_id:
                                user_id = self.env['res.users'].create({
                                    'login': signature,
                                    'name': signature,
                                    'employee_ids': [(0, 0, {
                                        'name': signature
                                    })]
                                })
                                _logger.info(f"Failed to find res.user with login {signature},"
                                             f" creating new user")

                            if msg_type == "delete":
                                # find office and remove it from office_ids
                                _logger.debug(f"Deleting office with office_code {office_code}"
                                              f" from user with login {signature}")
                                if office_id:
                                    for employee in user_id.employee_ids:
                                        employee.write({
                                            'office_ids': [(3, office_id.id, 0)]
                                        })
                                else:
                                    _logger.error(f"Failed to find hr.department"
                                                  f" with office_code {office_code}")
                            elif msg_type == "create":
                                # find office and add it to office_ids
                                _logger.debug(f"Adding office with office_code {office_code}"
                                              f" to user with login {signature}")
                                if office_id:
                                    for employee in user_id.employee_ids:
                                        employee.write({
                                            'office_ids': [(4, office_id.id, 0)]
                                        })
                                else:
                                    _logger.error(f"Failed to find hr.department"
                                                  f" with office_code {office_code}")
                            else:
                                _logger.info(f"Message of type {msg_type} not supported, ignoring")

                            # append message to ack_list to let main
                            # thread know that this can be ACK'd
                            with lock:
                                ack_list.append(message)
                        message = False
                    except:
                        _logger.exception(
                            "Officer MQ Sender: error while finding user!"
                        )
                else:
                    # slow down so we don't loop all the time
                    time.sleep(1)
        # close our new cursor
        env_new.cr.close()

    @api.model
    def mq_officer_listener(self, minutes_to_live=10):
        _logger.info("Officer MQ Listener started.")
        host_port = self.__get_host_port()
        target = self.env["ir.config_parameter"].get_param(
            "users_mq_ipf.target_officer",
            "/queue/Consumer.crm.VirtualTopic.handlaggarbehorighet.notifiering",
        )
        usr = self.env["ir.config_parameter"].get_param("users_mq_ipf.mquser", "dafa")
        pwd = self.env["ir.config_parameter"].get_param(
            "users_mq_ipf.mqpwd", "topsecret"
        )
        stomp_log_level = self.env["ir.config_parameter"].get_param(
            "users_mq_ipf.stomp_logger", "INFO"
        )

        # decide the stomper log level depending on param
        stomp_logger = logging.getLogger("stomp.py")
        stomp_logger.setLevel(getattr(logging, stomp_log_level))

        mqconn = stomp.Connection10(host_port)

        if (
            self.env["ir.config_parameter"].get_param("users_mq_ipf.mqusessl", "1")
            == "1"
        ):
            mqconn.set_ssl(for_hosts=host_port, ssl_version=ssl.PROTOCOL_TLS)
            _logger.debug("Officer MQ Listener - Using TLS")
        else:
            _logger.debug("Officer MQ Listener - Not using TLS")

        officerlsnr = OfficerListener(mqconn, usr, pwd, target, 4)
        mqconn.set_listener("", officerlsnr)
        # passing a bool in do_list to indicate if we should keep
        # running mq_officer_sender. What is a better solution?
        do_list = [True]
        try:
            connect_and_subscribe(mqconn, usr, pwd, target)

            counter = 12 * minutes_to_live  # Number of 5 sek slices to wait
            # define common lists to be used between threads
            msg_list = []
            ack_list = []

            # define a lock so we can lock msg_list while updating it
            # in each thread.
            lock = threading.Lock()
            # create a new thread running mq_officer_sender function
            sender_thread = threading.Thread(
                target=self.mq_officer_sender, args=(msg_list, ack_list, do_list, lock)
            )
            sender_thread.start()

            processed_list = []
            # run loop
            while counter > 0:
                # Let messages accumulate
                time.sleep(5)
                _logger.debug(
                    "__msglist before unsubscribe: %s" % officerlsnr.get_list()
                )
                # check if we have ACKs to send out
                with lock:
                    while ack_list:
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
                                    for msg in officerlsnr.get_list()
                                    if msg[0]["message-id"]
                                    == ack_message[0]["message-id"]
                                ),
                                False,
                            )
                            if not ack_message_current:
                                # this message ghosted us????
                                _logger.warn(
                                    "Officer MQ Listener - COULD NOT FIND MESSAGE TO ACC: %s"
                                    % ack_message[0]["message-id"]
                                )
                            else:
                                _logger.debug(
                                    "Officer MQ Listener - ACK: %s"
                                    % ack_message_current[0]["message-id"]
                                )
                                officerlsnr.ack_message(ack_message_current)
                            ack_message_current = False
                            ack_message = False
                        except:
                            _logger.exception("Officer MQ Listener: error ACK")
                # Stop listening
                mqconn.unsubscribe(target)

                # Handle list of messages
                for message in officerlsnr.get_list():
                    if message[0]["message-id"] not in processed_list:
                        try:
                            with lock:
                                _logger.info(f"Officer MQ Listener - adding message to internal queue: "
                                             f"message-id {message[0]['message-id']}, signature: {message[1].get(SIGN)}, "
                                             f"office code: {message[1].get(CODE)}")
                                msg_list.append(message)
                            # append message to processed_list to keep
                            # track of what messages have been processed
                            # this is needed since we will recieve already
                            # processed messages until they are ACK'd
                            processed_list.append(message[0]["message-id"])
                        except:
                            _logger.exception(
                                "Officer MQ Listener: error adding message to internal queue"
                            )
                message = False
                self.env.cr.commit()
                # Clear accumulated messages
                officerlsnr.clear_list()
                # Check if stop has been called
                cronstop = self.env["ir.config_parameter"].get_param(
                    "users_mq_ipf.cronstop", "0"
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
