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
from odoo.addons.af_process_log.models.af_process_log import MaxTriesExceededError


import json
import logging
import stomp
import ssl
from queue import Queue, Empty
from time import time

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
AISF_OFFICER_OFFICE_SYNC_PROCESS = "AIS-F OFFICER-OFFICE SYNC"
OFFICER_OFFICE_SYNC = "OFFICER-OFFICE SYNC"

class OfficerListener(stomp.ConnectionListener):
    def __init__(self, mqconn, user, pwd, target, clientid=4):
        self.__conn = mqconn
        self.__user = user
        self.__pwd = pwd
        self.__target = target
        self.__clientid = clientid
        self.__msgqueue = Queue()

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
            # Add message to queue
            self.__msgqueue.put((headers, data))

    def next_message(self, block=False, timeout=5):
        """Fetch the next message in the queue."""
        try:
            return self.__msgqueue.get(block=block, timeout=timeout)
        except Empty:
            return

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
    def mq_officer_listener(self, minutes_to_live=10):
        _logger.info("Officer MQ Listener started.")
        host_port = self.__get_host_port()
        target = self.env["ir.config_parameter"].get_param(
            "users_mq_ipf.target_officer",
            "/queue/Consumer.crm.VirtualTopic.handlaggarbehorighet.notifiering",
        )
        usr = self.env["ir.config_parameter"].get_param("users_mq_ipf.mquser", "crm")
        pwd = self.env["ir.config_parameter"].get_param(
            "users_mq_ipf.mqpwd", "topsecret"
        )
        stomp_log_level = self.env["ir.config_parameter"].get_param(
            "users_mq_ipf.stomp_logger", "INFO"
        )

        # decide the stomper log level depending on param
        stomp_logger = logging.getLogger("stomp.py")
        stomp_logger.setLevel(getattr(logging, stomp_log_level))

        log = self.env['af.process.log']

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
        try:
            connect_and_subscribe(mqconn, usr, pwd, target)

            limit = time() + minutes_to_live * 60

            while time() < limit:
                message = officerlsnr.next_message()
                if message:
                    env_new = None
                    try:
                        self.env['af.process.log'].log_message(
                            AISF_OFFICER_OFFICE_SYNC_PROCESS, message[0]["message-id"], "PROCESS INITIATED",
                            message=str(message), first=True)
                        new_cr = registry(self.env.cr.dbname).cursor()
                        uid, context = self.env.uid, self.env.context
                        with api.Environment.manage():
                            env_new = api.Environment(new_cr, uid, context)
                            if message:
                                _logger.debug("Officer MQ Sender: finding user")
                            headers, msg = message
                            signature = msg.get(SIGN)
                            office_code = msg.get(CODE)
                            msg_type = msg.get(TYPE)
                            access = msg.get(ACCESS)
                            eventid = headers["message-id"]
                            objectid = f"{signature}-{office_code}"
                            _logger.debug(f"Got message with  {signature}, "
                                          f"office code {office_code}, "
                                          f"type {msg_type}, "
                                          f"access {access}")
                            # not sure how specific the search has to be to find the right object
                            log.log_message(AISF_OFFICER_OFFICE_SYNC_PROCESS, eventid, "SYNC STARTED", objectid=objectid)
                            user_id = env_new['res.users'].search([('login', '=', signature)])
                            office_id = env_new['hr.department'].search([('office_code', '=', office_code)])
                            if not user_id:
                                user_id = env_new['res.users'].create({
                                    'login': signature,
                                    'name': signature,
                                    'employee_ids': [(0, 0, {
                                        'name': signature
                                    })]
                                })
                                log.log_message(AISF_OFFICER_OFFICE_SYNC_PROCESS, eventid,
                                                OFFICER_OFFICE_SYNC, objectid=objectid,
                                                info_3=f"Failed to find res.user"
                                                        f" with login {signature}, "
                                                        f"creating new user")
                                _logger.info(f"Failed to find res.user with login {signature},"
                                             f" creating new user")
                            if not office_id:
                                office_id = env_new['hr.department'].create({
                                    'name': office_code,
                                    'office_code': office_code
                                })
                                for employee in user_id.employee_ids:
                                    employee.write({
                                        'office_ids': [(4, office_id.id, 0)]
                                    })
                                log.log_message(AISF_OFFICER_OFFICE_SYNC_PROCESS, eventid,
                                                OFFICER_OFFICE_SYNC, objectid=objectid,
                                                info_2=f"Failed to find hr.department "
                                                       f"with office_code {office_code}, "
                                                       f"creating new")
                                _logger.error(f"Failed to find hr.department"
                                              f" with office_code {office_code},"
                                              f" creating new")
                            if msg_type == "delete":
                                # find office and remove it from office_ids
                                _logger.debug(f"Deleting office with office_code {office_code}"
                                              f" from user with login {signature}")
                                log.log_message(AISF_OFFICER_OFFICE_SYNC_PROCESS, eventid,
                                                OFFICER_OFFICE_SYNC, objectid=objectid,
                                                message=f"Deleting office with office_code {office_code}"
                                                        f" from user with login {signature}")
                                for employee in user_id.employee_ids:
                                    employee.write({
                                        'office_ids': [(3, office_id.id, 0)]
                                    })
                            elif msg_type == "create":
                                # find office and add it to office_ids
                                log.log_message(AISF_OFFICER_OFFICE_SYNC_PROCESS, eventid,
                                                OFFICER_OFFICE_SYNC, objectid=objectid,
                                                message=f"Adding office with office_code {office_code}"
                                                        f" to user with login {signature}")
                                _logger.debug(f"Adding office with office_code {office_code}"
                                              f" to user with login {signature}")
                                for employee in user_id.employee_ids:
                                    employee.write({
                                        'office_ids': [(4, office_id.id, 0)]
                                    })
                            else:
                                log.log_message(AISF_OFFICER_OFFICE_SYNC_PROCESS, eventid,
                                                OFFICER_OFFICE_SYNC, objectid=objectid,
                                                message=f"Message of type {msg_type} not supported,"
                                                        f" ignoring",
                                                status=False)
                                _logger.info(f"Message of type {msg_type} not supported, ignoring")
                    except MaxTriesExceededError:
                        # TODO: Check if we should NACK instead.
                        officerlsnr.ack_message(message)
                    except Exception as e:
                        _logger.exception(
                            f"Officer MQ Sender: error {e}"
                        )
                        log.log_message(AISF_OFFICER_OFFICE_SYNC_PROCESS, eventid,
                                        OFFICER_OFFICE_SYNC, objectid=objectid,
                                        error_message=f"Officer MQ Sender: error {e}",
                                        status=False)
                    finally:
                        # close our new cursor
                        if env_new:
                            env_new.cr.commit()
                            env_new.cr.close()
                # Check if stop has been called
                self.env.cr.commit()
                cronstop = self.env["ir.config_parameter"].get_param(
                    "users_mq_ipf.cronstop", "0")
                if cronstop != "0":
                    break
            # Stop listening
            mqconn.unsubscribe(target)
        except:
            _logger.exception("Something went wrong in MQ")
        finally:
            # send signal to stop other thread
            if mqconn.is_connected():
                mqconn.disconnect()
