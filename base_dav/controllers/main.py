# Copyright 2018 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import sys
import logging
import werkzeug
from odoo import http
from odoo.http import request

try:
    import radicale
    import radicale.app
    import radicale.config
except ImportError:
    radicale = None

PREFIX = '/.dav'
_logger = logging.getLogger(__name__)


class Main(http.Controller):

    @http.route(
        ['/.well-known/carddav', '/.well-known/caldav', '/.well-known/webdav'],
        type='http', auth='none', csrf=False,
    )
    def handle_well_known_request(self):
        return werkzeug.utils.redirect(PREFIX, 301)

    @http.route(
        [PREFIX, '%s/<path:davpath>' % PREFIX], type='http', auth='none',
        csrf=False,
    )
    def handle_dav_request(self, davpath=None):
        if radicale is None:
            return http.Response('radicale not installed', status=500)

        configuration = radicale.config.load()
        configuration.update(
            {
                "auth": {
                    "type": "odoo.addons.base_dav.radicale.auth",
                },
                "storage": {
                    "type": "odoo.addons.base_dav.radicale.collection",
                },
                "rights": {
                    "type": "odoo.addons.base_dav.radicale.rights",
                },
                "web": {
                    "type": "none",
                },
            },
            "odoo base_dav config",
        )

        application = radicale.app.Application(configuration)

        response_holder = {}

        def start_response(status, headers):
            response_holder['status'] = status
            response_holder['headers'] = headers

        environ = dict(
            request.httprequest.environ,
            HTTP_X_SCRIPT_NAME=PREFIX,
            PATH_INFO='/' + (davpath or ''),
            **({'wsgi.errors': sys.stderr}
               if 'wsgi.errors' not in request.httprequest.environ else {}),
        )

        result = application(environ, start_response)

        status = response_holder.get('status', '500 Internal Server Error')
        headers = response_holder.get('headers', [])

        response = http.Response(
            status=status,
            headers=dict(headers),
        )
        response.stream.write(b''.join(result))
        return response
