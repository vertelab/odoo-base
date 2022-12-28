# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
try:
    from paramiko import Transport
    from paramiko.transport import DEFAULT_WINDOW_SIZE, DEFAULT_MAX_PACKET_SIZE
except ImportError:
    pass
from odoo import api, SUPERUSER_ID
from odoo.modules.registry import Registry


class DocumentSFTPTransport(Transport):
    def __init__(
        self, cr, sock, default_window_size=DEFAULT_WINDOW_SIZE,
        default_max_packet_size=DEFAULT_MAX_PACKET_SIZE, gss_kex=False,
        gss_deleg_creds=True
    ):
        self.cr = cr
        super(DocumentSFTPTransport, self).__init__(
            sock, default_window_size=default_window_size,
            default_max_packet_size=default_max_packet_size, gss_kex=gss_kex,
            gss_deleg_creds=gss_deleg_creds
        )

    def run(self):
        with api.Environment.manage():
            self.env = api.Environment(self.cr, SUPERUSER_ID, {})
            result = super(DocumentSFTPTransport, self).run()
        return result
