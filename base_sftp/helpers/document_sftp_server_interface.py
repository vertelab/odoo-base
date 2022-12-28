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
from paramiko.common import o644, o777
from .document_sftp_sftp_server import StubSFTPHandle

_logger = logging.getLogger(__name__)


class DocumentSFTPSftpServerInterface(SFTPServerInterface):
    ROOT = os.path.expanduser('/tmp')

    def __init__(self, server, env):
        self.env = api.Environment(env.cr, server.env.user.id, env.context)

    def _realpath(self, file_path):
        return self.canonicalize(file_path)

    def list_folder(self, file_path):
        """
            list_folder: is responsible for the display of folders and files in the /tmp dir
            os.listdir: lists all directories, the filter used in the loop can be improved
        """
        if not file_path or file_path in ('/', '.'):
            file_path = self._realpath(self.ROOT)
        else:
            file_path = self._realpath(self.ROOT + file_path)
        try:
            out = []
            flist = os.listdir(file_path)
            for fname in flist:
                attr = SFTPAttributes.from_stat(os.stat(os.path.join(file_path, fname)))
                attr.filename = fname
                out.append(attr)
            return out
        except OSError as e:
            return SFTPServer.convert_errno(e.errno)

    def stat(self, file_path):
        """os.stat return an SFTPAttributes object for a path on the server,"""
        file_path = self._realpath(self.ROOT + file_path)
        try:
            return SFTPAttributes.from_stat(os.stat(file_path))
        except OSError as e:
            return SFTPServer.convert_errno(e.errno)

    def lstat(self, file_path):
        """Retrieve information about a file on the remote system, without shortcuts"""
        file_path = self._realpath(self.ROOT + file_path)
        try:
            return SFTPAttributes.from_stat(os.lstat(file_path))
        except OSError as e:
            return SFTPServer.convert_errno(e.errno)

    def open(self, f_path, flags, attr):
        x_path = self._realpath(self.ROOT + f_path)
        fd = os.open(x_path, os.O_CREAT | os.O_RDWR)
        try:
            f = os.fdopen(fd, "wb+")
        except OSError as e:
            _logger.info("Error: %s", e)
            return SFTPServer.convert_errno(e.errno)

        fobj = StubSFTPHandle(self.env, x_path, flags)
        fobj.filename = x_path
        fobj.readfile = f
        fobj.writefile = f

        return fobj

    def remove(self, file_path):
        if not file_path or file_path in ('/', '.'):
            file_path = self._realpath(self.ROOT)
        else:
            file_path = self._realpath(self.ROOT + file_path)
        try:
            stfp_handle = StubSFTPHandle(env=self.env, doc_path=file_path)
            stfp_handle._odoo_file_sync(action="Unlink")
            self.env.cr.commit()
            os.remove(file_path)
        except OSError as e:
            return SFTPServer.convert_errno(e.errno)
        return SFTP_OK

    def rename(self, old_path, new_path):
        """responsible for renaming file on the remote sever."""
        old_path = self._realpath(self.ROOT + old_path)
        new_path = self._realpath(self.ROOT + new_path)
        try:
            os.rename(old_path, new_path)
        except OSError as e:
            return SFTPServer.convert_errno(e.errno)
        return SFTP_OK

    def mkdir(self, file_path, attr):
        """responsible for creating directory on the remote sever. no relationship with odoo yet"""
        file_path = self._realpath(self.ROOT + file_path)
        try:
            os.mkdir(file_path)
            SFTPServer.set_file_attr(file_path, attr)
        except OSError as e:
            return SFTPServer.convert_errno(e.errno)
        return SFTP_OK

    def rmdir(self, dir_path):
        """responsible for deleting directory on the remote sever. no relationship with odoo yet"""
        dir_path = self._realpath(self.ROOT + dir_path)
        try:
            os.rmdir(dir_path)
        except OSError as e:
            return SFTPServer.convert_errno(e.errno)
        return SFTP_OK

    def session_ended(self):
        self.env.cr.close()
        return super(DocumentSFTPSftpServerInterface, self).session_ended()

    def session_started(self):
        self.env = self.env(cr=self.env.registry.cursor())
        self.ROOT = f"{self.ROOT}/{self.env.user.login}"
        if not path.exists(self.ROOT):
            os.mkdir(self.ROOT, mode=o777)
        os.chmod(self.ROOT, mode=o777)
        self._download_attachment(self.ROOT, data=self._fetch_attachments())

    def _download_attachment(self, x_path, data):
        for dir_data in data:
            dms_directory_file = f"{x_path}/{dir_data.name}"
            with open(dms_directory_file, 'wb') as f:
                stream = base64.b64decode(dir_data.datas)
                f.write(stream)

    def _fetch_attachments(self):
        attachments = self.env['ir.attachment']
        if attachments.check_access_rights('read', raise_exception=False):
            attachments = attachments.with_user(self.env.user).search([])
        return attachments
