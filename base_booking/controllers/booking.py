# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
import pytz
import re

from pytz.exceptions import UnknownTimeZoneError

from babel.dates import format_datetime, format_date, format_time
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from markupsafe import Markup
from urllib.parse import quote, unquote_plus
from werkzeug.exceptions import Forbidden, NotFound
from werkzeug.urls import url_encode

from odoo import Command, exceptions, http, fields, _
from odoo.http import request, route
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as dtf, email_normalize
from odoo.tools.mail import is_html_empty
from odoo.tools.misc import babel_locale_parse, get_lang
from odoo.addons.base.models.ir_qweb import keep_query
from odoo.addons.base.models.res_partner import _tz_get
from odoo.addons.phone_validation.tools import phone_validation
from odoo.exceptions import UserError



class BookingController(http.Controller):

    # ------------------------------------------------------------
    # BOOKING INVITATION
    # ------------------------------------------------------------

    @route(['/book/<string:short_code>'],
            type='http', auth="public", website=True)
    def booking_invite(self, short_code):
        """
        Invitation link that simplify the URL sent or shared to partners.
        This will redirect to a correct URL with the params selected with the
        invitation.
        """
        invitation = request.env['booking.invite'].sudo().search([('short_code', '=', short_code)])
        if not invitation:
            raise NotFound()
        return request.redirect(invitation.redirect_url)

    # ------------------------------------------------------------
    # APPOINTMENT INDEX PAGE
    # ------------------------------------------------------------

    @route(['/calendar', '/calendar/page/<int:page>'],
            type='http', auth="public", website=True, sitemap=True)
    def booking_type_index_old(self, page=1, **kwargs):
        """ For backward compatibility """
        return request.redirect(
            '/booking%s?%s' % ('/page/%s' % page if page != 1 else '', url_encode(kwargs)),
            code=301,
        )

