# -*- coding: utf-8 -*-
# © 2023 Vertel AB <http://vertel.se>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
try:
    from paramiko.common import AUTH_SUCCESSFUL, AUTH_FAILED, \
        OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED, OPEN_SUCCEEDED
    from paramiko import RSAKey, ServerInterface, SSHClient, Auth
    from paramiko.py3compat import decodebytes
    from paramiko.auth_handler import AuthHandler
except ImportError:
    pass


class CustomAuthHandler(AuthHandler):
    def auth_password(self, username, password, event):
        print("auth baba")
        self.transport.lock.acquire()
        try:
            self.auth_event = event
            self.auth_method = "password"
            self.username = username
            self.password = password
            self._request_auth()
        finally:
            self.transport.lock.release()
