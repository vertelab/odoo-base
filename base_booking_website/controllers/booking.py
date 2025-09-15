# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request

from odoo.addons.base.models.ir_qweb import keep_query
from odoo.addons.base_booking.controllers.booking import BookingController
from odoo.osv import expression


class WebsiteBooking(BookingController):

    # ------------------------------------------------------------
    # BOOKING INDEX PAGE
    # ------------------------------------------------------------

    @http.route()
    def booking_type_index(self, page=1, **kwargs):
        """
        Display the bookings to choose (the display depends of a custom option called 'Card Design')

        :param page: the page number displayed when the bookings are organized by cards

        A param filter_booking_type_ids can be passed to display a define selection of bookings types.
        This param is propagated through templates to allow people to go back with the initial booking
        types filter selection
        """
        kwargs['domain'] = self._bookings_base_domain(
            filter_booking_type_ids=kwargs.get('filter_booking_type_ids'),
            search=kwargs.get('search'),
            invite_token=kwargs.get('invite_token'),
            additional_domain=self._booking_website_domain(),
        )
        available_booking_types = self._fetch_and_check_private_booking_types(
            kwargs.get('filter_booking_type_ids'),
            kwargs.get('filter_staff_user_ids'),
            kwargs.get('filter_resource_ids'),
            kwargs.get('invite_token'),
            domain=kwargs['domain'],
        )
        if len(available_booking_types) == 1 and not kwargs.get('search'):
            # If there is only one booking type available in the selection, skip the booking type selection view
            return request.redirect('/booking/%s?%s' % (available_booking_types.id, keep_query('*')))

        cards_layout = request.website.viewref('base_booking_website.opt_bookings_list_cards').active

        if cards_layout:
            return request.render(
                'base_booking_website.bookings_cards_layout',
                self._prepare_bookings_cards_data(
                    page, available_booking_types,
                    **kwargs
                )
            )
        else:
            return request.render(
                'base_booking.bookings_list_layout',
                self._prepare_bookings_list_data(
                    available_booking_types,
                    **kwargs
                )
            )

    # ----------------------------------------------------------------
    # BOOKING TYPE PAGE VIEW : WITH NEW OPERATOR SELECTION VIEW
    # ----------------------------------------------------------------

    def _get_booking_type_resource_selection_view(self, booking_type, page_values):
        """
        Renders the booking_select_operator template. This displays a card view of available staff users to
        select from for booking_type, containing their picture, job description and website_description.

        :param booking_type: the booking_type that we want to access.
        :param page_values: dict of precomputed values in the booking_page route.
        """
        return request.render("base_booking_website.booking_select_operator", {
            'booking_type': booking_type,
            'available_bookings': page_values['available_bookings'],
            'main_object': booking_type,
            'users_possible': page_values['users_possible'],
            'resources_possible': page_values['resources_possible'],
        })

    def _get_booking_type_page_view(self, booking_type, page_values, state=False, **kwargs):
        """
        Override: when website_booking is installed, instead of the default booking type page, renders the
        operator selection template, if the condition below is met.
        """
        # If the user skips the resource selection to see all availabilities, make sure we do not show the selection.
        # As the operator view is mainly user cards, we only show it if avatars are 'on'. Also, it makes no sense in
        # random booking types since it is a selection screen. Moreover, the selection should not have already
        # been made before in order to avoid loops. Finally, in order to choose, one needs at least 2 possible users/resources.
        skip_resource_selection = kwargs.get('skip_resource_selection') or \
            not booking_type.active or \
            booking_type.assign_method != 'resource_time' or \
            booking_type.avatars_display != 'show'
        operator_selection = not skip_resource_selection and \
            booking_type.schedule_based_on == 'users' and \
            not page_values['user_selected'] and \
            len(page_values['users_possible']) > 1
        resource_selection = not skip_resource_selection and \
            booking_type.schedule_based_on == 'resources' and \
            not page_values['resource_selected'] and \
            len(page_values['resources_possible']) > 1
        if operator_selection or resource_selection:
            return self._get_booking_type_resource_selection_view(booking_type, page_values)
        return super()._get_booking_type_page_view(booking_type, page_values, state, **kwargs)

    def _prepare_booking_type_page_values(self, booking_type, staff_user_id=False, resource_selected_id=False, skip_resource_selection=False, **kwargs):
        """
        Override: Take into account the operator selection flow. When skipping the selection,
        no {user,resource}_selected or user_default should be set. The display is also properly managed according to this new flow.

        :param skip_resource_selection: If true, skip the selection, and instead see all availabilities. No user should be selected.
        """
        values = super()._prepare_booking_type_page_values(booking_type, staff_user_id, resource_selected_id, **kwargs)
        values['skip_resource_selection'] = skip_resource_selection
        if skip_resource_selection:
            values['user_selected'] = values['user_default'] = request.env['res.users']
            values['resource_selected'] = request.env['booking.resource']
        else:
            resource_or_user_selected = values['user_selected'] if booking_type.schedule_based_on == 'users' else values['resource_selected']
            values['hide_select_dropdown'] = values['hide_select_dropdown'] or (
                booking_type.avatars_display == 'show' and resource_or_user_selected and booking_type.assign_method != 'time_resource')
        return values

    # Tools / Data preparation
    # ------------------------------------------------------------

    def _prepare_bookings_cards_data(self, page, booking_types, **kwargs):
        """
            Compute specific data for the cards layout like the search bar and the pager.
        """
        BOOKINGS_PER_PAGE = 12
        website = request.website
        booking_count = len(booking_types)

        pager = website.pager(
            url='/booking',
            url_args=kwargs,
            total=booking_count,
            page=page,
            step=BOOKINGS_PER_PAGE,
            scope=5,
        )
        booking_types = booking_types.sorted('is_published', reverse=True)[pager['offset']:pager['offset'] + BOOKINGS_PER_PAGE]

        return {
            'booking_types': booking_types,
            'current_search': kwargs.get('search'),
            'pager': pager,
            'filter_booking_type_ids': kwargs.get('filter_booking_type_ids'),
            'filter_staff_user_ids': kwargs.get('filter_staff_user_ids'),
            'invite_token': kwargs.get('invite_token'),
            'search_count': booking_count,
        }

    def _get_allowed_companies(self, organizer):
        """ Check if the current website can be used to determine the company
        and fallback on the companies of the organizer if not """
        companies = super()._get_allowed_companies(organizer)
        website_company = request.website.company_id if request.website else request.env['res.company']
        return website_company if website_company in companies else companies

    def _get_customer_partner(self):
        partner = super()._get_customer_partner()
        if not partner:
            partner = request.env['website.visitor']._get_visitor_from_request().partner_id
        return partner

    @staticmethod
    def _get_customer_country():
        """
            Find the country from the geoip lib or fallback on the user or the visitor
        """
        country = BookingController._get_customer_country()
        if not country:
            visitor = request.env['website.visitor']._get_visitor_from_request()
            country = visitor.country_id
        return country

    @classmethod
    def _bookings_base_domain(cls, filter_booking_type_ids, search=False, invite_token=False, additional_domain=None):
        domain = super()._bookings_base_domain(filter_booking_type_ids, search, invite_token, additional_domain)
        domain = expression.AND([domain, ['|', ('website_id', '=', request.website.id), ('website_id', '=', False)]])
        return domain
