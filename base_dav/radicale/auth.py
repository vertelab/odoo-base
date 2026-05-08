# Copyright 2018 Therp BV <https://therp.nl>
# Copyright 2019-2020 initOS GmbH <https://initos.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging

from odoo.http import request

try:
    from radicale.auth import BaseAuth
except ImportError:
    BaseAuth = object

logger = logging.getLogger(__name__)


class Auth(BaseAuth):

    def __init__(self, configuration):
        super().__init__(configuration)

    def _login(self, login, password):
        env = request.env
        try:
            uid = env['res.users']._login(
                env.cr.dbname,
                {'type': 'password', 'login': login, 'password': password},
                user_agent_env={'interactive': False},
            )
            uid = uid.get('uid') if isinstance(uid, dict) else uid
        except Exception:
            logger.debug('DAV auth failed for %s', login, exc_info=True)
            return ""
        if uid:
            request._env = env(user=uid)
            return login
        return ""
