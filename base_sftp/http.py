import datetime
import decimal
import json
import logging
import sys
import traceback
from collections import defaultdict

from werkzeug.exceptions import (
    BadRequest,
    Forbidden,
    HTTPException,
    InternalServerError,
    NotFound,
    Unauthorized,
)
from werkzeug.utils import escape

import odoo
from odoo.exceptions import (
    AccessDenied,
    AccessError,
    MissingError,
    UserError,
    ValidationError,
)
import socket
from odoo.http import HttpRequest, Root, SessionExpiredException, request, db_list
from odoo.tools import ustr
from odoo import fields, models, _
from odoo.tools.config import config

_logger = logging.getLogger(__name__)

parent_setup_session = Root.setup_session


def get_config(param, msg):
    value = odoo.tools.config.get(param, False)
    if not value:
        raise UserError(_("%s (%s in /etc/odoo/odoo.conf)" % (msg, param)))
    return value


def setup_session(self, httprequest):

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    host, port = get_config('sftp_bind', 'localhost:0').split(':')

    try:
        _logger.info('Monkey path Binding to %s:%s', host, port)
        server_socket.bind((host, int(port)))
    except socket.error as e:
        _logger.info('Monkey path Server %s:%s is already running', host, port)

    host_real, port_real = server_socket.getsockname()
    _logger.info('Monkey path Listening to SFTP connections on %s:%s', host_real, port_real)
    server_socket.listen(5)
    server_socket.settimeout(2)

    return parent_setup_session(self, httprequest)


Root.setup_session = setup_session
