import stomp
import sys
import time
import ssl
from odoointf import odoointf
from message import parse_message


class AsokListener(stomp.ConnectionListener):
    _debug = False
    __conn = None
    __target = None
    __host = None
    __port = None
    __user = None
    __pwd = None
    __ssl = 0
    __keepgoing = True

    # parameterized constructor
    def __init__(self, host, port, target, user=None, pwd=None, ssl=0):
        self.__host = host
        self.__port = port
        self.__target = target
        self.__user = user
        self.__pwd = pwd
        self.__ssl = ssl
        print("%s:%s - %s" % ( host, port, target))

    def print(self, message):
        print(message)

    def debug_print(self, message):
        if self._debug >= 1:
            print(message)

    def handle_message(self, message):
        import xmltodict

        odoo_obj = odoointf()

        xmlobj = parse_message(message)

        self.debug_print(xmlobj)
        data = xmlobj["msg"]
        self.debug_print("Try to call odoo_obj m_%s" % data["data"])

        result = odoo_obj(data["data"], data["key"])
        if result:
            # Handle the result from the call
            self.print("Alles gut mit anruf!")
            pass
        else:
            self.print("Anruf fehlt!")


    def handle_json_message(self, message):
        import json

#         message = """[
#     {
#         "pnr": "121212-1212",
#         "stom_track": 0,
#         "stom_description": "Låg risk för behov av stöd och matchning."
#     },
#     {
#         "pnr": "121212-1212",
#         "stom_track": 1,
#         "stom_description": "Grundläggande stöd och matchning med eller utan språkstöd."
#     },
#     {
#         "pnr": "121212-1212",
#         "stom_track": 2,
#         "stom_description": "Förstärkt stöd och matchning med eller utan spåkstöd."
#     }
# ]"""
        try:
            # Assume JSON
            stom_list = json.loads(message)
            # Assume list of dicts or get exception
            the_ones = list(filter(lambda s: s["stom_track"] == 1, stom_list))
        except:
            print("Invalid JSON format %s" % message)
            return

        if the_ones and len(the_ones) > 0:
            # Handle the result from the call
            self.print("Alles gut mit anruf!")
            self.print(the_ones)
        else:
            self.print("Anruf fehlt!")
        
        
    
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
        print("Connecting: {0}".format(host_and_port))

    def on_connected(self, headers, body):
        """
        Called by the STOMP connection when a CONNECTED frame is
        received (after a connection has been established or
        re-established).

        :param dict headers: a dictionary containing all headers sent by the server as key/value pairs.
        :param body: the frame's payload. This is usually empty for CONNECTED frames.
        """
        print("Connected: %s - %s" % (headers, body))

    def on_message(self, headers, msg):
        self.debug_print("on_message: {0} - {1}".format(msg, headers["message-id"]))
        self.handle_json_message(msg)
        self.print("HAndle message done")
        self.__conn.ack(headers["message-id"])
    
    def on_error(self, headers, body):
        """
        Called by the STOMP connection when an ERROR frame is received.

        :param dict headers: a dictionary containing all headers sent by the server as key/value pairs.
        :param body: the frame's payload - usually a detailed error description.
        """
        print("Error: %s - %s" % (headers, body))

    def listen(self):
        self.print("Listening on %s:%s %s" % (self.__host, self.__port, self.__target))
        self.__conn = stomp.Connection10([(self.__host, self.__port)])

        self.print("MHXXX ssl: %s : %s" % (type(self.__ssl), self.__ssl))

        if self.__ssl != "0":
            self.__conn.set_ssl(for_hosts=[(self.__host, self.__port)], ssl_version=ssl.PROTOCOL_TLS)
            self.print("Using SSL")

        self.__conn.set_listener("AsokListener", self)
        #self.__conn.start()
        self.__conn.connect(self.__user, self.__pwd, wait=True)
        self.__conn.subscribe(self.__target, id=4, ack="client")
        try:
            while self.__keepgoing:
                time.sleep(1)
        finally:
            self.__conn.unsubscribe(self.__target)
            time.sleep(1)
            self.__conn.disconnect()
            self.debug_print("Stopped")

    @property
    def dbglevel(self):
        return self._debug

    @dbglevel.setter
    def dbglevel(self, value):
        try:
            self._debug = int(value)
        except:
            self._debug = 0

    @dbglevel.deleter
    def name(self):
        del self._debug

    def stop(self):
        self.debug_print("Stopping ...")
        self.__keepgoing = False
