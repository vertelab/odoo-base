import string
from odoo import models, fields, api, _
import os
import base64

ROOT_DIR = os.path.expanduser('/tmp')


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    def _storage_location(self):
        sftp_storage_location = f"{ROOT_DIR}/{self.env.user.login}"
        return sftp_storage_location

    def _sync_with_sftp(self, path_names, content):
        """
        Synchronize the file with the SFTP server. ir.attachment(10, )
        """
        if path_names:
            path = f"{self._storage_location()}/{path_names}"
            with open(path, 'wb') as f:
                stream = base64.b64decode(content)
                f.write(stream)

    def write(self, vals):
        full_path = f"{self._storage_location()}/{self.name}"
        if vals and os.path.exists(full_path):
            os.remove(path=full_path)
        rec = super(IrAttachment, self).write(vals)
        if vals.get('datas') or vals.get('name'):
            self._sync_with_sftp(path_names=self.name, content=self.datas)
        return rec

    @api.model
    def create(self, vals):
        res = super(IrAttachment, self).create(vals)
        if vals.get('datas'):
            self._sync_with_sftp(path_names=res.name, content=res.datas)
        return res

    def unlink(self, os_delete=True):
        for rec in self:
            path = f"{self._storage_location()}/{rec.name}"
            if path and os.path.exists(path) and os_delete:
                os.remove(f"{path}")
        return super(IrAttachment, self).unlink()
