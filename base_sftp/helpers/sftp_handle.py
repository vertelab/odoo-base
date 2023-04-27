# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
try:
    from paramiko import SFTPServerInterface, SFTPServer, SFTPAttributes, SFTPHandle
    from paramiko.sftp import SFTP_OK
except ImportError:
    pass
from email.mime import base
from odoo import api
import os, stat
import os.path
from os import path
import base64
import logging
import traceback
import tempfile
from odoo.modules.registry import Registry

from paramiko.common import o644, o777

_logger = logging.getLogger(__name__)


class BaseSFTPHandle(SFTPHandle):

    def __init__(self, env, doc_path, flags=0):
        self.env = env
        self.doc_path = doc_path
        self.flags = flags
        super(BaseSFTPHandle, self).__init__(flags)

    def write(self, offset, data):
        res = super().write(offset, data)
        self._odoo_file_sync(data=open(self.doc_path, 'rb').read(), action="CreateWrite")
        return res

    def _database_name(self, db_dir_path=None):
        db_name = db_dir_path.split("/")
        db_name = [valid_ord for valid_ord in db_name if valid_ord]
        return db_name[1]

    def _odoo_file_sync(self, data=None, action=None):
        try:
            folder_path, file_name = os.path.split(self.doc_path)  # ('/tmp/Media', 'goat.jpeg')

            db_registry = Registry.new(self._database_name(folder_path))
            with api.Environment.manage(), db_registry.cursor() as cr:
                self.env = api.Environment(cr, self.env.user.id, {})

                if not file_name.startswith('.'):
                    # self.env.cr.fetchall()

                    file_obj = self.env['ir.attachment'].with_user(self.env.user).search(
                        [('name', '=', file_name)], limit=1)

                    if file_obj and action == "Unlink":
                        os_delete = False
                        file_obj.unlink(os_delete)
                    elif not file_obj and action == "CreateWrite":
                        self.env['ir.attachment'].with_user(self.env.user).create({
                            'name': file_name,
                            'type': "binary",
                            'datas': base64.b64encode(data),
                        })
                    elif file_obj and action == "CreateWrite":
                        file_obj.with_user(self.env.user).write({
                            'datas': base64.b64encode(data),
                        })
                    self.env.cr.commit()
        except OSError as e:
            _logger.info("Exception: %s", e)
            return SFTPServer.convert_errno(e.errno)


class BaseSFTPServer(SFTPServer):
    def start_subsystem(self, name, transport, channel):
        with api.Environment.manage():
            return super(BaseSFTPServer, self).start_subsystem(name, transport, channel)
