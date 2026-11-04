# Copyright 2018 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import sys
import logging
# import werkzeug  # oanvänd efter att well-known-routen avregistrerats
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

    # ── well-known: AVREGISTRERAD (2026-10-25) ────────────────────────
    #
    # Den här routen svarade 301 på /.well-known/{caldav,carddav,webdav}
    # och skickade klienten till /.dav (radicale-spåret). Den konkurrerade
    # därför ut calendar_caldav, som äger den kompletta CalDAV-/
    # CardDAV-servern. Eftersom DAVx5, Thunderbird och GNOME Online
    # Accounts börjar med formen UTAN avslutande snedstreck vann den här
    # routen varje gång — klienten hamnade i radicale-spåret och fick en
    # tom kalender.
    #
    # /.well-known/* ägs nu av calendar_caldav (båda formerna, båda
    # protokollen). /.dav finns kvar nedan så att redan konfigurerade
    # klienter inte slutar fungera under övergången.
    #
    # Återaktivera INTE utan att samtidigt avregistrera calendar_caldavs
    # well-known-routes — annars är konflikten tillbaka.

    # ── /.dav: AVREGISTRERAD (2026-10-25, steg 5) ─────────────────────
    #
    # Även om well-known pekar rätt kan en klient som redan har /.dav som
    # server-URL fortsätta hamra mot radicale-spåret. Den svarade 207 med
    # en tom multistatus (176 B) var 30:e minut för DAVx5, Thunderbird och
    # Evolution. calendar_caldav äger protokollet nu; /.dav ska ge 404 så
    # att en gammal klientkonfiguration syns som ett fel i stället för en
    # tyst tom kalender.
    #
    # Rutten lämnas i koden (avkommenterad) för att den ska gå att slå på
    # igen vid behov — men den registreras inte.
    #
    # @http.route(
    #     [PREFIX, '%s/<path:davpath>' % PREFIX], type='http', auth='none',
    #     csrf=False,
    # )
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

        # Odoo strips every 'wsgi.*' key out of httprequest.environ (see
        # HTTPRequest.__init__ in odoo/http.py), keeping only 'wsgi.url_scheme'.
        # Radicale is a WSGI application and reads the request body straight
        # from environ['wsgi.input'], so without it every request carrying a
        # body fails with KeyError: 'wsgi.input' -> HTTP 500. The symptom is
        # that OPTIONS succeeds (no body) while PROPFIND fails, which makes
        # DAVx5 report "Couldn't find CalDAV or CardDAV service".
        # Re-add the stream from the unfiltered environ (same accessor Odoo
        # itself uses in http.py:Request._set_request_dispatcher).
        raw_environ = getattr(
            request.httprequest, '_HTTPRequest__environ', {}) or {}
        environ = dict(
            request.httprequest.environ,
            HTTP_X_SCRIPT_NAME=PREFIX,
            PATH_INFO='/' + (davpath or ''),
            **({'wsgi.errors': sys.stderr}
               if 'wsgi.errors' not in request.httprequest.environ else {}),
            **({'wsgi.input': raw_environ['wsgi.input']}
               if raw_environ.get('wsgi.input') is not None
               and 'wsgi.input' not in request.httprequest.environ else {}),
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
