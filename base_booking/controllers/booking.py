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


def _formated_weekdays(locale):
    """ Return the weekdays' name for the current locale
        from Mon to Sun.
        :param locale: locale
    """
    formated_days = [
        format_date(date(2021, 3, day), 'EEE', locale=locale)
        for day in range(1, 8)
    ]
    # Get the first weekday based on the lang used on the website
    first_weekday_index = babel_locale_parse(locale).first_week_day
    # Reorder the list of days to match with the first weekday
    formated_days = list(formated_days[first_weekday_index:] + formated_days)[:7]
    return formated_days


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

    @route(['/booking', '/booking/page/<int:page>'],
           type='http', auth="public", website=True, sitemap=True)
    def booking_type_index(self, page=1, **kwargs):
        """
        Display the bookings to choose (the display depends of a custom option called 'Card Design')

        :param page: the page number displayed when the bookings are organized by cards

        A param filter_booking_type_ids can be passed to display a define selection of bookings types.
        This param is propagated through templates to allow people to go back with the initial booking
        types filter selection
        """
        kwargs['domain'] = self._booking_website_domain()
        return request.render('booking.bookings_list_layout', self._prepare_bookings_list_data(**kwargs))

    # Tools / Data preparation
    # ------------------------------------------------------------

    def _prepare_bookings_list_data(self, booking_types=None, **kwargs):
        """Compute specific data used to render the list layout

        :param recordset booking_types: Record set of bookings to show.
            If not provided, fetch them using _fetch_and_check_private_booking_types
        """

        booking_types = booking_types or self._fetch_and_check_private_booking_types(
            kwargs.get('filter_booking_type_ids'),
            kwargs.get('filter_staff_user_ids'),
            kwargs.get('filter_resource_ids'),
            kwargs.get('invite_token'),
            domain=self._bookings_base_domain(
                filter_booking_type_ids=kwargs.get('filter_booking_type_ids'),
                search=kwargs.get('search'),
                invite_token=kwargs.get('invite_token'),
                additional_domain=kwargs.get('domain')
            )
        )
        booking_types = booking_types.sorted('is_published', reverse=True)
        return {
            'booking_types': booking_types,
            'invite_token': kwargs.get('invite_token'),
            'filter_booking_type_ids': kwargs.get('filter_booking_type_ids'),
            'filter_staff_user_ids': kwargs.get('filter_staff_user_ids'),
            'filter_resource_ids': kwargs.get('filter_resource_ids'),
        }

    @classmethod
    def _bookings_base_domain(cls, filter_booking_type_ids, search=False, invite_token=False, additional_domain=None):
        """
        Generate a domain for booking filtering.
        This method constructs a domain to filter booking records based on various criteria.
        Args:
            filter_booking_type_ids (str): A comma-separated string of booking type IDs to filter by.
                Example: "1,2,3"
            search (str, optional): A search string to filter bookings by name (case-insensitive).
            invite_token (bool, optional): A boolean flag indicating whether to include invite token filtering.
                If False, it considers the user's country and published status of bookings.
            additional_domain (list, optional): Additional domain expressions to include in the filter.
        Returns:
            list: A list of domain expressions suitable for use in Odoo record filtering.
        """

        domain = list(additional_domain) if additional_domain else []
        if filter_booking_type_ids:
            filter_booking_type_ids = unquote_plus(filter_booking_type_ids)
            domain = expression.AND([domain, [('id', 'in', json.loads(filter_booking_type_ids))]])

        if not invite_token:
            country = cls._get_customer_country()
            if country:
                country_domain = ['|', ('country_ids', '=', False), ('country_ids', 'in', [country.id])]
                domain = expression.AND([domain, country_domain])

        # Add domain related to the search bar
        if search:
            domain = expression.AND([domain, [('name', 'ilike', search)]])

        # Because of sudo search, we need to search only published ones if there is no invite_token
        if request.env.user.share and not invite_token:
            domain = expression.AND([domain, [('is_published', '=', True)]])

        return domain

    def _booking_website_domain(self):
        return [
            '|', ('end_datetime', '=', False), ('end_datetime', '>=', datetime.utcnow())
        ]

    # ------------------------------------------------------------
    # APPOINTMENT TYPE PAGE VIEW
    # ------------------------------------------------------------

    @route(['/calendar/<string:booking_type>'],
            type='http', auth="public", website=True, sitemap=True)
    def booking_type_page_old(self, booking_type, **kwargs):
        """ For backward compatibility:
        booking_type is transformed from a recordset to a string because we removed the rights for public user.
        """
        return request.redirect('/booking/%s?%s' % (request.env['ir.http']._unslug(booking_type)[1], keep_query('*')), code=301)

    @route(['/booking/<int:booking_type_id>'],
           type='http', auth="public", website=True, sitemap=True)
    def booking_type_page(self, booking_type_id, state=False, staff_user_id=False, resource_selected_id=False, **kwargs):
        """
        This route renders the booking page: It first computes a dict of values useful for all potential
        views and to choose between them in _get_booking_type_page_view, that renders the chosen one.

        :param booking_type_id: the booking_type_id of the booking type that we want to access
        :param state: the type of message that will be displayed in case of an error/info. Possible values:
            - cancel: Info message to confirm that an booking has been canceled
            - failed-staff-user: Error message displayed when the slot has been taken while doing the registration
        :param staff_user_id: id of the selected user, from upstream or coming back from an error.
        :param resource_selected_id: id of the selected resource, from upstream or coming back from an error.
        """
        kwargs['domain'] = self._bookings_base_domain(
            filter_booking_type_ids=kwargs.get('filter_booking_type_ids'),
            search=kwargs.get('search'),
            invite_token=kwargs.get('invite_token'),
            additional_domain=kwargs.get('domain')
        )
        available_bookings = self._fetch_and_check_private_booking_types(
            kwargs.get('filter_booking_type_ids'),
            kwargs.get('filter_staff_user_ids'),
            kwargs.get('filter_resource_ids'),
            kwargs.get('invite_token'),
            domain=kwargs['domain']
        )
        booking_type = available_bookings.filtered(lambda appt: appt.id == int(booking_type_id))

        kwargs['available_bookings'] = available_bookings
        if not booking_type:
            raise NotFound()

        page_values = self._prepare_booking_type_page_values(booking_type, staff_user_id, resource_selected_id, **kwargs)
        return self._get_booking_type_page_view(booking_type, page_values, state, **kwargs)

    def _get_slots_from_filter(self, booking_type, filter_records, asked_capacity=1):
        """
        Compute the slots and the first month that has available slots from the given filter.

        :param booking_type: the booking type that we want to access.
        :param filter_records: users/resources that are used to compute the slots
        :param asked_capacity: the capacity asked by the user
        :return: a dict containing:
            - slots: the available slots
            - month_first_available: the first month that has available slots or False if there is none
        """
        slots = booking_type._get_booking_slots(
            request.session['timezone'],
            filter_users=filter_records if booking_type.schedule_based_on == "users" else None,
            filter_resources=filter_records if booking_type.schedule_based_on == "resources" else None,
            asked_capacity=asked_capacity,
        )
        return {
            'slots': slots,
            'month_first_available': next((month['id'] for month in slots if month['has_availabilities']), False),
        }

    def _get_slots_values(self, booking_type, selected_filter_record, default_filter_record, possible_filter_records, asked_capacity=1):
        """
        Compute the slots and the first month that has available slots from the given filters.

        :param booking_type: the booking type that we want to access.
        :param selected_filter_record: the selected users/resources
        :param default_filter_record: the default users/resources
        :param possible_filter_records: the possible users/resources
        :param asked_capacity: the capacity asked by the user
        :return: a dict containing:
            - slots: the available slots
            - month_first_available: the first month that has available slots or False if there is none
        """
        if selected_filter_record:
            return self._get_slots_from_filter(booking_type, selected_filter_record, asked_capacity)

        if not default_filter_record:
            return self._get_slots_from_filter(booking_type, possible_filter_records, asked_capacity)

        ordered_filters = default_filter_record | possible_filter_records
        for current_filter in ordered_filters:
            values = self._get_slots_from_filter(booking_type, current_filter, asked_capacity)
            if values['month_first_available'] is not False:
                if booking_type.schedule_based_on == "users":
                    values['user_selected'] = current_filter
                else:
                    values['resource_selected'] = current_filter
                return values
        return values

    def _get_booking_type_page_view(self, booking_type, page_values, state=False, **kwargs):
        """
        Renders the booking information alongside the calendar for the slot selection, after computation of
        the slots and preparation of other values, depending on the arguments values. This is the method to override
        in order to select another view for the booking page.

        :param booking_type: the booking type that we want to access.
        :param page_values: dict containing common booking page values. See _prepare_booking_type_page_values for details.
        :param state: the type of message that will be displayed in case of an error/info. See booking_type_page.
        """
        request.session.timezone = self._get_default_timezone(booking_type)
        asked_capacity = int(kwargs.get('asked_capacity', 1))
        filter_prefix = 'user' if booking_type.schedule_based_on == "users" else 'resource'
        slots_values = self._get_slots_values(booking_type,
            selected_filter_record=page_values[f'{filter_prefix}_selected'],
            default_filter_record=page_values[f'{filter_prefix}_default'],
            possible_filter_records=page_values[f'{filter_prefix}s_possible'],
            asked_capacity=asked_capacity)
        formated_days = _formated_weekdays(get_lang(request.env).code)

        render_params = {
            'booking_type': booking_type,
            'is_html_empty': is_html_empty,
            'formated_days': formated_days,
            'main_object': booking_type,
            'month_kept_from_update': False,
            'state': state,
            'timezone': request.session['timezone'],  # bw compatibility
            **page_values,
            **slots_values,
        }
        # Do not let the browser store the page, this ensures correct timezone and params management in case
        # the user goes back and forth to this endpoint using browser controls (or mouse back button)
        # this is especially necessary as we alter the request.session parameters.
        return request.render("base_booking.booking_info", render_params, headers={'Cache-Control': 'no-store'})

    def _prepare_booking_type_page_values(self, booking_type, staff_user_id=False, resource_selected_id=False, **kwargs):
        """ Computes all values needed to choose between / common to all booking_type page templates.

        :return: a dict containing:
            - available_bookings: all available bookings according to current filters and invite tokens.
            - filter_booking_type_ids, filter_staff_user_ids and invite_token parameters.
            - user_default: the first of possible staff users. It will be selected by default (in the user select dropdown)
            if no user_selected. Otherwise, the latter will be preselected instead. It is only set if there is at least one
            possible user and the choice is activated in booking_type, or used for having the user name in title if there
            is a single possible user, for random selection.
            - user_selected: the user corresponding to staff_user_id in the url and to the selected one. It can be selected
            upstream, from the operator_select screen (see WebsiteAppointment controller), or coming back from an error.
            It is only set if among the possible users.
            - users_possible: all possible staff users considering filter_staff_user_ids and staff members of booking_type.
            - resource_selected: the resource corresponding to resource_selected_id in the url and to the selected one. It can be selected
            upstream, from the operator_select screen (see WebsiteAppointment controller), or coming back from an error.
            - resources_possible: all possible resources considering filter_resource_ids and resources of booking type.
            - max_capacity: the maximum capacity that can be selected by the user to make an booking on a resource.
            - hide_select_dropdown: True if the user select dropdown should be hidden. (e.g. an operator has been selected before)
            Even if hidden, it can still be in the view and used to update availabilities according to the selected user in the js.
        """
        filter_staff_user_ids = json.loads(kwargs.get('filter_staff_user_ids') or '[]')
        filter_resource_ids = json.loads(kwargs.get('filter_resource_ids') or '[]')
        users_possible = self._get_possible_staff_users(booking_type, filter_staff_user_ids)
        resources_possible = self._get_possible_resources(booking_type, filter_resource_ids)
        user_default = user_selected = request.env['res.users']
        resource_default = resource_selected = request.env['booking.resource']
        staff_user_id = int(staff_user_id) if staff_user_id else False
        resource_selected_id = int(resource_selected_id) if resource_selected_id else False

        if booking_type.schedule_based_on == 'users':
            if booking_type.assign_method == 'resource_time' and users_possible:
                if staff_user_id and staff_user_id in users_possible.ids:
                    user_selected = request.env['res.users'].sudo().browse(staff_user_id)
                user_default = users_possible[0]
            elif booking_type.assign_method == 'time_auto_assign' and len(users_possible) == 1:
                user_default = users_possible[0]
        elif resources_possible:
            if resource_selected_id and resource_selected_id in resources_possible.ids and booking_type.assign_method != 'time_resource':
                resource_selected = request.env['booking.resource'].sudo().browse(resource_selected_id)
            elif booking_type.assign_method == 'resource_time':
                resource_default = resources_possible[0]
        possible_combinations = (resource_selected or resource_default or resources_possible)._get_filtered_possible_capacity_combinations(1, {})
        max_capacity_possible = possible_combinations[-1][1] if possible_combinations else 1

        return {
            'asked_capacity': int(kwargs['asked_capacity']) if kwargs.get('asked_capacity') else False,
            'available_bookings': kwargs['available_bookings'],
            'filter_booking_type_ids': kwargs.get('filter_booking_type_ids'),
            'filter_staff_user_ids': kwargs.get('filter_staff_user_ids'),
            'filter_resource_ids': kwargs.get('filter_resource_ids'),
            'hide_select_dropdown': len(users_possible if booking_type.schedule_based_on == 'users' else resources_possible) <= 1,
            'invite_token': kwargs.get('invite_token'),
            'max_capacity': min(12, max_capacity_possible),
            'resource_default': resource_default,
            'resource_selected': resource_selected,
            'resources_possible': resources_possible,
            'user_default': user_default,
            'user_selected': user_selected,
            'users_possible': users_possible,
        }

    # Staff User tools
    # ------------------------------------------------------------

    @http.route('/booking/<int:booking_type_id>/avatar', type='http', auth="public", cors="*")
    def booking_staff_user_avatar(self, booking_type_id, user_id=False, avatar_size=512):
        """
        Route used to bypass complicated access rights like 'website_published'. We consider we can display the avatar
        of the user of id user_id if it belongs to the booking_type_id and if the option avatars_display is set to 'show'
        for that booking type. In that case we consider that the avatars can be made public. Default field is avatar_512.
        Another avatar_size corresponding to an existing avatar field on res.users can be given as route parameter.
        """
        user = request.env['res.users'].sudo().browse(int(user_id))
        booking_type = request.env['booking.type'].sudo().browse(booking_type_id)

        user = user if booking_type.avatars_display == 'show' and user in booking_type.staff_user_ids else request.env['res.users']
        return request.env['ir.binary']._get_image_stream_from(
            user,
            field_name='avatar_%s' % (avatar_size if int(avatar_size) in [128, 256, 512, 1024, 1920] else 512),
            placeholder='mail/static/src/img/smiley/avatar.jpg',
        ).get_response()

    def _get_possible_resources(self, booking_type, filter_resource_ids):
        """
        This method filters the resources of given booking_type using filter_resource_ids that are possible to pick.
        If no filter exist and assign method is different than 'time_auto_assign', we allow all resources existing on the booking type.

        :param booking_type_id: the booking_type_id of the booking type that we want to access
        :param filter_resource_ids: list of resource ids used to filter the ones of the booking_types.
        :return: an booking.resource recordset containing all possible resources to choose from.
        """
        if not filter_resource_ids:
            return booking_type.resource_ids
        return booking_type.resource_ids.filtered(lambda resource: resource.id in filter_resource_ids)

    def _get_possible_staff_users(self, booking_type, filter_staff_user_ids):
        """
        This method filters the staff members of given booking_type using filter_staff_user_ids that are possible to pick.
        If no filter exist and assign method is different than 'time_auto_assign', we allow all users existing on the booking type.

        :param booking_type_id: the booking_type_id of the booking type that we want to access
        :param filter_staff_user_ids: list of user ids used to filter the ones of the booking_type.
        :return: a res.users recordset containing all possible staff users to choose from.
        """
        if not filter_staff_user_ids:
            return booking_type.staff_user_ids
        return booking_type.staff_user_ids.filtered(lambda staff_user: staff_user.id in filter_staff_user_ids)

    # Resource tools
    # ------------------------------------------------------------

    @http.route('/booking/<int:booking_type_id>/resource_avatar', type='http', auth="public")
    def booking_resource_avatar(self, booking_type_id, resource_id=False, avatar_size=512):
        """
        Route used to bypass access rights on the booking resource for public user.
        Equivalent of ``booking_staff_user_avatar()`` for booking resource.
        """
        resource = request.env['booking.resource'].sudo().browse(int(resource_id))
        booking_type = request.env['booking.type'].sudo().browse(booking_type_id)

        resource = resource if booking_type.avatars_display == 'show' and resource in booking_type.resource_ids else request.env['booking.resource']
        return request.env['ir.binary']._get_image_stream_from(
            resource,
            field_name='avatar_%s' % (avatar_size if int(avatar_size) in [128, 256, 512, 1024, 1920] else 512),
        ).get_response()

    # Tools / Data preparation
    # ------------------------------------------------------------

    @staticmethod
    def _fetch_and_check_private_booking_types(booking_type_ids, staff_user_ids, resource_ids, invite_token, domain=False):
        """
        When an invite_token is in the params, we need to check if the params used and the ones in the invitation are
        the same.
        For the old link, we use the technical field "is_published" to determine if a user had previous access.
        Check finally if we have the rights on the booking_types. If the token is correct then we continue, if not
        we raise an Forbidden error. We return the current booking type displayed/used if one or the booking types
        linked to the filter in the url param
        :param str booking_type_ids: list of booking type ids for the filter linked to the booking types in a string format
        :param str staff_user_ids: list of user ids for the filter linked to the staff users in a string format
        :param str resource_ids: list of resource ids for the filter linked to the resources in a string format
        :param str invite_token: token of the booking invite
        :param domain: a search domain used when displaying the available booking types
        """
        booking_type_ids = json.loads(unquote_plus(booking_type_ids or "[]"))
        if not booking_type_ids and domain is not False:
            booking_type_ids = request.env['booking.type'].sudo().search(domain).ids
        elif not booking_type_ids:
            raise ValueError()

        booking_types = request.env['booking.type'].browse(booking_type_ids).exists()
        staff_users = request.env['res.users'].sudo().browse(json.loads(unquote_plus(staff_user_ids or "[]")))
        resources = request.env['booking.resource'].sudo().browse(json.loads(unquote_plus(resource_ids or "[]")))

        if invite_token:
            appt_invite = request.env['booking.invite'].sudo().search([('access_token', '=', invite_token)])
            if not appt_invite or not appt_invite._check_bookings_params(booking_types, staff_users, resources):
                raise Forbidden()
            # To bypass the access checks in case we are public user
            booking_types = booking_types.sudo()
        elif request.env.user.share:
            # Backward compatibility for old version that had their booking types "published" by default (aka accessible with read access rights)
            booking_types = booking_types.sudo().filtered('is_published') or booking_types

        if not booking_types.browse().has_access('read'):
            raise Forbidden()
        booking_types = booking_types._filtered_access('read')

        if domain:
            booking_types = booking_types.filtered_domain(domain)
        return booking_types

    # ------------------------------------------------------------
    # APPOINTMENT TYPE BOOKING
    # ------------------------------------------------------------

    @http.route(['/booking/<int:booking_type_id>/info'],
                type='http', auth="public", website=True, sitemap=False)
    def booking_type_id_form(self, booking_type_id, date_time, duration, staff_user_id=None, resource_selected_id=None, available_resource_ids=None, asked_capacity=1, **kwargs):
        """
        Render the form to get information about the user for the booking

        :param booking_type_id: the booking type id related
        :param date_time: the slot datetime selected for the booking
        :param duration: the duration of the slot
        :param staff_user_id: the user selected for the booking
        :param resource_selected_id: the resource selected for the booking
        :param available_resource_ids: the resources info we want to propagate that are linked to the slot time
        :param asked_capacity: the asked capacity for the booking
        :param filter_booking_type_ids: see ``Appointment.bookings()`` route
        """
        domain = self._bookings_base_domain(
            filter_booking_type_ids=kwargs.get('filter_booking_type_ids'),
            search=kwargs.get('search'),
            invite_token=kwargs.get('invite_token')
        )
        available_bookings = self._fetch_and_check_private_booking_types(
            kwargs.get('filter_booking_type_ids'),
            kwargs.get('filter_staff_user_ids'),
            kwargs.get('filter_resource_ids'),
            kwargs.get('invite_token'),
            domain=domain,
        )
        booking_type = available_bookings.filtered(lambda appt: appt.id == int(booking_type_id))

        if not booking_type:
            raise NotFound()

        if not self._check_booking_is_valid_slot(booking_type, staff_user_id, resource_selected_id, available_resource_ids, date_time, duration, asked_capacity, **kwargs):
            raise NotFound()

        partner = self._get_customer_partner()
        partner_data = partner.read(fields=['name', 'phone', 'email'])[0] if partner else {}
        date_time = unquote_plus(date_time)
        date_time_object = datetime.strptime(date_time, dtf)
        day_name = format_datetime(date_time_object, 'EEE', locale=get_lang(request.env).code)
        date_formated = format_date(date_time_object.date(), locale=get_lang(request.env).code)
        time_locale = format_time(date_time_object.time(), locale=get_lang(request.env).code, format='short')
        resource = request.env['booking.resource'].sudo().browse(int(resource_selected_id)) if resource_selected_id else request.env['booking.resource']
        staff_user = request.env['res.users'].browse(int(staff_user_id)) if staff_user_id else request.env['res.users']
        users_possible = self._get_possible_staff_users(
            booking_type,
            json.loads(unquote_plus(kwargs.get('filter_staff_user_ids') or '[]')),
        )
        resources_possible = self._get_possible_resources(
            booking_type,
            json.loads(unquote_plus(kwargs.get('filter_resource_ids') or '[]')),
        )
        return request.render("base_booking.booking_form", {
            'partner_data': partner_data,
            'booking_type': booking_type,
            'available_bookings': available_bookings,
            'main_object': booking_type,
            'datetime': date_time,
            'date_locale': f'{day_name} {date_formated}',
            'time_locale': time_locale,
            'datetime_str': date_time,
            'duration_str': duration,
            'duration': float(duration),
            'staff_user': staff_user,
            'resource': resource,
            'asked_capacity': int(asked_capacity),
            'timezone': request.session.get('timezone') or booking_type.booking_tz,  # bw compatibility
            'users_possible': users_possible,
            'resources_possible': resources_possible,
            'available_resource_ids': available_resource_ids,
            'login_with_redirect_url': f'/web/login?redirect={quote(request.httprequest.full_path)}',
        })

    def _check_booking_is_valid_slot(self, booking_type, staff_user_id, resource_selected_id, available_resource_ids, start_dt, duration, asked_capacity, **kwargs):
        """
        Given slot parameters check it is still valid, based on staff_user/resource
        availability, slot boundaries, ...
        :param record booking_type: an booking.type record under which
          the booking is about to be taken;
        :param str(int) staff_user_id: staff_user linked to the booking slot;
        :param str(int) resource_selected_id: resource chosen by the customer;
        :param str(list) available_resource_ids: list of resources ids available for the slots
        :param datetime start_dt: booking slot starting datetime that will be
          localized in customer timezone;
        :param str(float) duration: the duration of the booking;
        :param str(int) asked_capacity: the capacity asked by the customer;
        """
        if not booking_type or not start_dt or not duration:
            return False
        if booking_type.schedule_based_on == 'users' and not staff_user_id:
            return False
        if booking_type.schedule_based_on == 'resources' and not resource_selected_id and not available_resource_ids:
            return False

        staff_user = None
        resources = None
        try:
            duration = float(duration)
            asked_capacity = int(asked_capacity)
            staff_user_id = int(staff_user_id) if staff_user_id else False
            resource_selected_id = int(resource_selected_id) if resource_selected_id else False
            available_resource_ids = json.loads(unquote_plus(available_resource_ids)) if available_resource_ids else False
            start_dt = unquote_plus(start_dt)
        except ValueError:
            # Value Error: some parameters don't have the correct format
            # (duration:float, asked_capacity:int, staff_user_id:int, resource_selected_id:int, available_resource_ids:list<int>, start_dt:str)
            return False

        try:
            session_tz = request.session.get('timezone', booking_type.booking_tz)
            tz_info = pytz.timezone(session_tz)
            start_dt_utc = tz_info.localize(fields.Datetime.from_string(start_dt)).astimezone(pytz.utc)
        except (ValueError, UnknownTimeZoneError):
            # ValueError: the datetime may be ill-formatted
            return False

        # we shouldn't be able to book an booking in the past
        if start_dt_utc < datetime.today().astimezone(pytz.utc):
            return False

        if booking_type.schedule_based_on == 'users':
            staff_user = request.env['res.users'].sudo().search([('id', '=', staff_user_id)])
        else:
            resources = request.env['booking.resource'].sudo().search([('id', 'in', available_resource_ids)])
            if resource_selected_id:
                resource = request.env['booking.resource'].sudo().search([('id', '=', resource_selected_id)])
                # Check that chosen resource exists and is part of resources available
                if not resource or resource not in resources:
                    return False

        return booking_type._check_booking_is_valid_slot(staff_user, resources, asked_capacity, session_tz, start_dt_utc, duration)

    @http.route(['/booking/<int:booking_type_id>/submit'],
                type='http', auth="public", website=True, methods=["POST"])
    def booking_form_submit(self, booking_type_id, datetime_str, duration_str, name, phone, email, staff_user_id=None, available_resource_ids=None, asked_capacity=1,
                                guest_emails_str=None, **kwargs):
        """
        Create the event for the booking and redirect on the validation page with a summary of the booking.

        :param booking_type_id: the booking type id related
        :param datetime_str: the string representing the datetime
        :param duration_str: the string representing the duration
        :param name: the name of the user sets in the form
        :param phone: the phone of the user sets in the form
        :param email: the email of the user sets in the form
        :param staff_user_id: the user selected for the booking
        :param available_resource_ids: the resources ids available for the booking
        :param asked_capacity: asked capacity for the booking
        :param str guest_emails: optional line-separated guest emails. It will
          fetch or create partners to add them as event attendees;
        """
        domain = self._bookings_base_domain(
            filter_booking_type_ids=kwargs.get('filter_booking_type_ids'),
            search=kwargs.get('search'),
            invite_token=kwargs.get('invite_token')
        )

        available_bookings = self._fetch_and_check_private_booking_types(
            kwargs.get('filter_booking_type_ids'),
            kwargs.get('filter_staff_user_ids'),
            kwargs.get('filter_resource_ids'),
            kwargs.get('invite_token'),
            domain=domain,
        )
        booking_type = available_bookings.filtered(lambda appt: appt.id == int(booking_type_id))

        if not booking_type:
            raise NotFound()
        timezone = request.session.get('timezone') or booking_type.booking_tz
        tz_session = pytz.timezone(timezone)
        datetime_str = unquote_plus(datetime_str)
        date_start = tz_session.localize(fields.Datetime.from_string(datetime_str)).astimezone(pytz.utc).replace(tzinfo=None)
        duration = float(duration_str)
        date_end = date_start + relativedelta(hours=duration)
        invite_token = kwargs.get('invite_token')

        staff_user = request.env['res.users']
        resources = request.env['booking.resource']
        resource_ids = None
        asked_capacity = int(asked_capacity)
        resources_remaining_capacity = None
        if booking_type.schedule_based_on == 'resources':
            resource_ids = json.loads(unquote_plus(available_resource_ids))
            # Check if there is still enough capacity (in case someone else booked with a resource in the meantime)
            resources = request.env['booking.resource'].sudo().browse(resource_ids).exists()
            if any(resource not in booking_type.resource_ids for resource in resources):
                raise NotFound()
            resources_remaining_capacity = booking_type._get_resources_remaining_capacity(resources, date_start, date_end, with_linked_resources=False)
            if resources_remaining_capacity['total_remaining_capacity'] < asked_capacity:
                return request.redirect('/booking/%s?%s' % (booking_type.id, keep_query('*', state='failed-resource')))
        else:
            # check availability of the selected user again (in case someone else booked while the client was entering the form)
            staff_user = request.env['res.users'].sudo().search([('id', '=', int(staff_user_id))])
            if staff_user not in booking_type.staff_user_ids:
                raise NotFound()
            if staff_user and not staff_user.partner_id.calendar_verify_availability(date_start, date_end):
                return request.redirect('/booking/%s?%s' % (booking_type.id, keep_query('*', state='failed-staff-user')))

        guests = None
        if booking_type.allow_guests:
            if guest_emails_str:
                guests = request.env['calendar.event'].sudo()._find_or_create_partners(guest_emails_str)

        customer = self._get_customer_partner()

        # email is mandatory
        new_customer = not customer.email
        if not new_customer and customer.email != email and customer.email_normalized != email_normalize(email):
            new_customer = True
        if not new_customer:
            # phone is mandatory
            if not customer.phone:
                customer.phone = customer._phone_format(number=phone) or phone
            else:
                customer_phone_fmt = customer._phone_format(fname="phone")
                input_country = self._get_customer_country()
                input_phone_fmt = phone_validation.phone_format(phone, input_country.code, input_country.phone_code, force_format="E164", raise_exception=False)
                new_customer = customer.phone != phone and customer_phone_fmt != input_phone_fmt

        if new_customer:
            customer = customer.sudo().create({
                'name': name,
                'phone': customer._phone_format(number=phone, country=self._get_customer_country()) or phone,
                'email': email,
                'lang': request.lang.code,
            })

        # partner_inputs dictionary structures all answer inputs received on the booking submission: key is question id, value
        # is answer id (as string) for choice questions, text input for text questions, array of ids for multiple choice questions.
        partner_inputs = {}
        booking_question_ids = booking_type.question_ids.ids
        for k_key, k_value in [item for item in kwargs.items() if item[1]]:
            question_id_str = re.match(r"\bquestion_([0-9]+)\b", k_key)
            if question_id_str and int(question_id_str.group(1)) in booking_question_ids:
                partner_inputs[int(question_id_str.group(1))] = k_value
                continue
            checkbox_ids_str = re.match(r"\bquestion_([0-9]+)_answer_([0-9]+)\b", k_key)
            if checkbox_ids_str:
                question_id, answer_id = [int(checkbox_ids_str.group(1)), int(checkbox_ids_str.group(2))]
                if question_id in booking_question_ids:
                    partner_inputs[question_id] = partner_inputs.get(question_id, []) + [answer_id]

        # The answer inputs will be created in _prepare_calendar_event_values from the values in answer_input_values
        answer_input_values = []
        base_answer_input_vals = {
            'booking_type_id': booking_type.id,
            'partner_id': customer.id,
        }

        for question in booking_type.question_ids.filtered(lambda question: question.id in partner_inputs.keys()):
            if question.question_type == 'checkbox':
                answers = question.answer_ids.filtered(lambda answer: answer.id in partner_inputs[question.id])
                answer_input_values.extend([
                    dict(base_answer_input_vals, question_id=question.id, value_answer_id=answer.id) for answer in answers
                ])
            elif question.question_type in ['select', 'radio']:
                answer_input_values.append(
                    dict(base_answer_input_vals, question_id=question.id, value_answer_id=int(partner_inputs[question.id]))
                )
            elif question.question_type in ['char', 'text']:
                answer_input_values.append(
                    dict(base_answer_input_vals, question_id=question.id, value_text_box=partner_inputs[question.id].strip())
                )

        booking_line_values = []
        if booking_type.schedule_based_on == 'resources':
            capacity_to_assign = asked_capacity
            for resource in resources:
                resource_remaining_capacity = resources_remaining_capacity.get(resource)
                new_capacity_reserved = min(resource_remaining_capacity, capacity_to_assign, resource.capacity)
                capacity_to_assign -= new_capacity_reserved
                booking_line_values.append({
                    'booking_resource_id': resource.id,
                    'capacity_reserved': new_capacity_reserved,
                    'capacity_used': new_capacity_reserved if resource.shareable and booking_type.resource_manage_capacity else resource.capacity,
                })

        if invite_token:
            booking_invite = request.env['booking.invite'].sudo().search([('access_token', '=', invite_token)])
        else:
            booking_invite = request.env['booking.invite']

        return self._handle_booking_form_submission(
            booking_type, date_start, date_end, duration, answer_input_values, name,
            customer, booking_invite, guests, staff_user, asked_capacity, booking_line_values
        )

    def _handle_booking_form_submission(
        self, booking_type,
        date_start, date_end, duration,  # booking boundaries
        answer_input_values, name, customer, booking_invite, guests=None,  # customer info
        staff_user=None, asked_capacity=1, booking_line_values=None  # booking staff / resources
    ):
        """ This method takes the output of the processing of booking's form submission and
            creates the event corresponding to those values. Meant for overrides to set values
            needed to set a specific redirection.

            :returns: a dict of useful values used in the redirection to next step
        """
        event = request.env['calendar.event'].with_context(
            mail_notify_author=True,
            mail_create_nolog=True,
            mail_create_nosubscribe=True,
            allowed_company_ids=self._get_allowed_companies(staff_user or booking_type.create_uid).ids,
        ).sudo().create({
            'booking_answer_input_ids': [Command.create(vals) for vals in answer_input_values],
            **booking_type._prepare_calendar_event_values(
                asked_capacity, booking_line_values, duration,
                booking_invite, guests, name, customer, staff_user, date_start, date_end
            )
        })
        return request.redirect(f"/calendar/view/{event.access_token}?partner_id={customer.id}&{keep_query('*', state='new')}")

    # Tools / Data preparation
    # ------------------------------------------------------------

    def _get_allowed_companies(self, organizer):
        """ Get the allowed companies of the organizer of the event
        :param: <res.users> organizer: the organizer of the event
        :return: recordset of res.company
        """
        return organizer.company_ids

    def _get_customer_partner(self):
        partner = request.env['res.partner']
        if not request.env.user._is_public():
            partner = request.env.user.partner_id
        return partner

    @staticmethod
    def _get_customer_country():
        """
            Find the country from the geoip lib or fallback on the user or the visitor
        """
        country = request.env['res.country']
        if request.geoip.country_code:
            country = country.search([('code', '=', request.geoip.country_code)])
        if not country:
            country = request.env.user.country_id if not request.env.user._is_public() else country
        return country

    def _get_default_timezone(self, booking_type):
        """
            Find the default timezone from the value store in the session. If not value is found,
            we check if a location is defined on the booking type and set the timezone based on
            the value set on the booking type. Otherwise we also check the cookies or fallback on the
            timezone of the booking type.
        """
        if 'timezone' in request.session:
            return request.session.timezone
        if booking_type.location_id:
            return booking_type.booking_tz
        cookie = request.cookies.get('tz')
        if cookie and cookie in dict(_tz_get(self)):
            return cookie
        return booking_type.booking_tz

    # ------------------------------------------------------------
    # APPOINTMENT TYPE JSON DATA
    # ------------------------------------------------------------

    @http.route(['/booking/get_upcoming_bookings'], type="json", auth="public")
    def get_upcoming_bookings(self, calendar_event_access_tokens=False):
        """ Get up to the next 20 upcoming bookings data based on either logged user or info given by list of calendar event tokens
        :param <list> calendar_event_access_tokens: list of booked booking access tokens.
            Uses if user is not logged to find upcoming bookings booked by the partner.
        :return: return upcoming data in the format: {
            'next_upcoming_booking': the next upcoming booking taken data (access_token, booker, booking_type, start),
            'valid_access_tokens': list of access token still available for the user (based on the booker id or the list of access token received)
                In case, the user is logged we return an empty list to not return private info.
        }
        """
        common_domain = [
          ('booking_type_id', '!=', False),
          ('start', '>', datetime.now()),
        ]
        if not request.env.user._is_public():
            domain = [('booking_booker_id', '=', request.env.user.partner_id.id)]
        else:
            domain = [('access_token', 'in', calendar_event_access_tokens)]
        upcoming_bookings = request.env['calendar.event'].sudo().search_read(
            expression.AND([common_domain, domain]),
            fields=['access_token', 'booking_booker_id', 'booking_type_id', 'start'],
            order="start",
            limit=20,
        )
        if not upcoming_bookings:
            return False
        return {
            'next_upcoming_booking': upcoming_bookings[0],
            'valid_access_tokens': [appt['access_token'] for appt in upcoming_bookings] if request.env.user._is_public() else [],
        }

    @http.route(['/booking/<int:booking_type_id>/get_message_intro'],
                type="json", auth="public", methods=['POST'], website=True)
    def get_booking_message_intro(self, booking_type_id, **kwargs):
        domain = self._bookings_base_domain(
            filter_booking_type_ids=kwargs.get('filter_booking_type_ids'),
            search=kwargs.get('search'),
            invite_token=kwargs.get('invite_token')
        )

        available_bookings = self._fetch_and_check_private_booking_types(
            kwargs.get('filter_booking_type_ids'),
            kwargs.get('filter_staff_user_ids'),
            kwargs.get('filter_resource_ids'),
            kwargs.get('invite_token'),
            domain=domain,
        )
        booking_type = available_bookings.filtered(lambda appt: appt.id == int(booking_type_id))

        if not booking_type:
            raise NotFound()

        return booking_type.message_intro or ''

    @http.route(['/booking/<int:booking_type_id>/update_available_slots'],
                type="json", auth="public", website=True)
    def booking_update_available_slots(self, booking_type_id, staff_user_id=None, resource_selected_id=None, asked_capacity=1, timezone=None, **kwargs):
        """
            Route called when the selected user or resource or asked_capacity or the timezone is modified to adapt the possible slots accordingly
        """
        domain = self._bookings_base_domain(
            filter_booking_type_ids=kwargs.get('filter_booking_type_ids'),
            search=kwargs.get('search'),
            invite_token=kwargs.get('invite_token')
        )

        available_bookings = self._fetch_and_check_private_booking_types(
            kwargs.get('filter_booking_type_ids'),
            kwargs.get('filter_staff_user_ids'),
            kwargs.get('filter_resource_ids'),
            kwargs.get('invite_token'),
            domain=domain,
        )
        booking_type = available_bookings.filtered(lambda appt: appt.id == int(booking_type_id))

        if not booking_type:
            raise ValueError()

        request.session['timezone'] = timezone or booking_type.booking_tz
        filter_staff_user_ids = json.loads(kwargs.get('filter_staff_user_ids') or '[]')
        filter_resource_ids = json.loads(kwargs.get('filter_resource_ids') or '[]')
        filter_users = filter_resources = False
        # If no staff_user_id is set, use only the filtered staff users to compute slots.
        if staff_user_id:
            filter_users = request.env['res.users'].sudo().browse(int(staff_user_id))
        elif resource_selected_id:
            filter_resources = request.env['booking.resource'].sudo().browse(int(resource_selected_id))
        else:
            filter_users = self._get_possible_staff_users(booking_type, filter_staff_user_ids)
            filter_resources = self._get_possible_resources(booking_type, filter_resource_ids)
        asked_capacity = int(asked_capacity)
        slots = booking_type._get_booking_slots(request.session['timezone'], filter_users, filter_resources, asked_capacity=asked_capacity)
        month_first_available = next((month['id'] for month in slots if month['has_availabilities']), False)
        month_before_update = kwargs.get('month_before_update')
        month_kept_from_update = next((month['id'] for month in slots if month['month'] == month_before_update), False) if month_before_update else False
        formated_days = _formated_weekdays(get_lang(request.env).code)

        return request.env['ir.qweb']._render('base_booking.booking_calendar', {
            'booking_type': booking_type,
            'available_bookings': available_bookings,
            'asked_capacity': asked_capacity,
            'timezone': request.session['timezone'],
            'formated_days': formated_days,
            'slots': slots,
            'month_kept_from_update': month_kept_from_update,
            'month_first_available': month_first_available,
        })
