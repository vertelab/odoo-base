# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
import socket
from io import StringIO, BytesIO
import threading
import paramiko

from odoo.service.server import server

from odoo import SUPERUSER_ID, api, models
from odoo.modules.registry import Registry

from ..helpers.document_sftp_transport import DocumentSFTPTransport
from ..helpers.document_sftp_server import DocumentSFTPServer
from ..helpers.document_sftp_sftp_server import DocumentSFTPSftpServer
from ..helpers.document_sftp_server_interface import DocumentSFTPSftpServerInterface


_db2thread = {}
_channels = []
_logger = logging.getLogger(__name__)


class DocumentSFTP(models.AbstractModel):
    _name = 'document.sftp'
    _description = 'SFTP server'

    def _run_server(self, dbname, stop):
        db_registry = Registry.new(dbname)
        with api.Environment.manage(), db_registry.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            env[self._name].__run_server(stop)

    @api.model
    def __run_server(self, stop):
        # this is heavily inspired by
        # https://github.com/rspivak/sftpserver/blob/master/src/sftpserver
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        host, port = self.env['ir.config_parameter'].get_param('sftp_bind', 'localhost:0').split(':')
        _logger.info('Binding to %s:%s', host, port)
        server_socket.bind((host, int(port)))
        host_real, port_real = server_socket.getsockname()
        _logger.info('Listening to SFTP connections on %s:%s', host_real, port_real)
        if host_real != host or port_real != port:
            self.env['ir.config_parameter'].set_param('sftp_bind', '%s:%s' % (host_real, port_real))
        server_socket.listen(5)
        server_socket.settimeout(2)

        while not stop.is_set():
            try:
                conn, addr = server_socket.accept()
            except socket.timeout:
                while _channels and not _channels[0].get_transport().is_active():
                    _channels.pop(0)
                continue

            key = self.env['ir.config_parameter'].get_param('sftp_host_key')
            host_key = paramiko.Ed25519Key.from_private_key(StringIO(key))

            transport = DocumentSFTPTransport(self.env.cr, conn)
            transport.add_server_key(host_key)
            transport.set_subsystem_handler('sftp', DocumentSFTPSftpServer, DocumentSFTPSftpServerInterface, self.env)
            server = DocumentSFTPServer(self.env)
            try:
                transport.start_server(server=server)
                channel = transport.accept()
                if channel:
                    _channels.append(channel)
            except (paramiko.SSHException, EOFError):
                continue

    def _register_hook(self):

        cr = self._cr
        dbname = cr.dbname
        if dbname not in _db2thread:
            stop = threading.Event()
            _db2thread[dbname] = (threading.Thread(target=self._run_server, args=(dbname, stop)), stop,)
            _db2thread[dbname][0].start()
            old_stop = server.stop

            def new_stop():
                stop.set()
                old_stop()

            server.stop = new_stop
        return super(DocumentSFTP, self)._register_hook()
