# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from operator import itemgetter

from odoo import http, _
from odoo.http import request
from odoo.osv.expression import AND, OR
from odoo.tools import groupby as groupbyelem

from odoo.addons.portal.controllers import portal
from odoo.addons.portal.controllers.portal import pager as portal_pager

class AppointmentPortal(portal.CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)

        if 'booking_count' in counters:
            domain = self._get_portal_default_domain()
            values['booking_count'] = request.env['calendar.event'].search_count(domain)

        return values

    def _get_portal_default_domain(self):
        my_user = request.env.user
        return [
            ('user_id', '!=', my_user.id),
            ('partner_ids', 'in', my_user.partner_id.ids),
            ('booking_type_id', '!=', False),
        ]

    def _get_booking_search_domain(self, search_in, search):
        search_domains = []
        if search_in in ('all', 'name'):
            search_domains.append([('name', 'ilike', search)])
        if search_in in ('all', 'responsible'):
            search_domains.append([('user_id', 'ilike', search)])
        if search_in in ('all', 'description'):
            search_domains.append([('description', 'ilike', search)])
        return OR(search_domains) if search_domains else []

    def _booking_get_groupby_mapping(self):
        return {
            'responsible': 'user_id',
        }

    @http.route(['/my/bookings',
                 '/my/bookings/page/<int:page>',
                ], type='http', auth='user', website=True)
    def portal_my_bookings(self, page=1, sortby=None, filterby=None, search=None, search_in='all', groupby='none', **kwargs):
        values = self._prepare_portal_layout_values()
        # Sudo to access the booking name and responsible for the groupby
        Event = request.env['calendar.event'].sudo()

        domain = self._get_portal_default_domain()

        searchbar_sortings = {
            'date': {'label': _('Date'), 'order': 'start'},
            'name': {'label': _('Name'), 'order': 'name'},
        }

        searchbar_inputs = {
            'all': {'label': _('Search in All'), 'input': 'all'},
            'name': {'label': _('Search in Name'), 'input': 'name'},
            'responsible': {'label': _('Search in Responsible'), 'input': 'responsible'},
            'description': {'label': _('Search in Description'), 'input': 'description'}
        }

        searchbar_groupby = {
            'none': {'label': _('None'), 'input': 'none'},
            'responsible': {'label': _('Responsible'), 'input': 'responsible'},
        }

        searchbar_filters = {
            'upcoming': {'label': _("Upcoming"), 'domain': [('start', '>=', datetime.today())]},
            'past': {'label': _("Past"), 'domain': [('start', '<', datetime.today())]},
            'all': {'label': _("All"), 'domain': []},
        }

        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']
        groupby_mapping = self._booking_get_groupby_mapping()
        groupby_field = groupby_mapping.get(groupby, None)
        if groupby_field is not None and groupby_field not in Event._fields:
            raise ValueError(_("The field '%s' does not exist in the targeted model", groupby_field))
        order = '%s, %s' % (groupby_field, sort_order) if groupby_field else sort_order

        if not filterby:
            filterby = 'all'
        domain = AND([domain, searchbar_filters[filterby]['domain']])

        if search and search_in and (search_domain := self._get_booking_search_domain(search_in, search)):
            domain = AND([domain, search_domain])

        booking_count = Event.search_count(domain)
        pager = portal_pager(
            url="/my/bookings",
            url_args={'sortby': sortby, 'search_in': search_in, 'search': search, 'groupby': groupby, 'filterby': filterby},
            total=booking_count,
            page=page,
            step=self._items_per_page
        )
        bookings = Event.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])

        grouped_bookings = False
        # If not False, this will contain a list of tuples (record of groupby, recordset of events):
        # [(res.users(2), calendar.event(1, 2)), (...), ...]
        if groupby_field:
            grouped_bookings = [(g, Event.concat(*events)) for g, events in groupbyelem(bookings, itemgetter(groupby_field))]

        values.update({
            'bookings': bookings,
            'grouped_bookings': grouped_bookings,
            'page_name': 'booking',
            'pager': pager,
            'default_url': '/my/bookings',
            'searchbar_sortings': searchbar_sortings,
            'search_in': search_in,
            'search': search,
            'sortby': sortby,
            'groupby': groupby,
            'filterby': filterby,
            'searchbar_inputs': searchbar_inputs,
            'searchbar_groupby': searchbar_groupby,
            'searchbar_filters': searchbar_filters,
        })
        return request.render("base_booking.portal_my_bookings", values)
