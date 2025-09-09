# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.addons.base.models.res_partner import _tz_get
from odoo.exceptions import ValidationError
import pandas as pd


class BookingType(models.Model):
    _name = "booking.type"
    _inherit = [
        'booking.type',
        'website.seo.metadata',
        'website.published.multi.mixin',
        'website.searchable.mixin',
    ]

    def _compute_website_url(self):
        super()._compute_website_url()
        for appointment_type in self:
            if appointment_type.id:
                appointment_type.website_url = '/booking/%s' % appointment_type.id
            else:
                appointment_type.website_url = False

    def create_and_get_website_url(self, **kwargs):
        if 'appointment_tz' not in kwargs:
            # appointment_tz is a mandatory field defaulting to the environment user's timezone
            # however, sometimes the current user timezone is not defined, let's use a fallback
            website_visitor = self.env['website.visitor']._get_visitor_from_request(force_create=False)
            kwargs['appointment_tz'] = self.env.user.tz or website_visitor.timezone or 'UTC'

        return super().create_and_get_website_url(**kwargs)

    def copy_data(self, default=None):
        """ Force False manually for all categories of appointment type when duplicating
        even for categories that should be auto-publish. """
        default = dict(default or {})
        default['is_published'] = False
        return super().copy_data(default=default)

    def get_backend_menu_id(self):
        return self.env.ref('calendar.mail_menu_calendar').id

    # @api.model
    # def _search_get_detail(self, website, order, options):
    #     invite_token = options.get('invite_token')
    #     allowed_appointment_type_ids = WebsiteAppointment._fetch_and_check_private_appointment_types(
    #         options.get('filter_appointment_type_ids'),
    #         options.get('filter_staff_user_ids'),
    #         options.get('filter_resource_ids'),
    #         invite_token,
    #         domain=WebsiteAppointment._appointments_base_domain(
    #             filter_appointment_type_ids=options.get('filter_appointment_type_ids'),
    #             search=options.get('search'),
    #             invite_token=invite_token,
    #             additional_domain=WebsiteAppointment._appointment_website_domain(self)
    #         )
    #     ).ids
    #
    #     domain = [[('id', 'in', allowed_appointment_type_ids)]]
    #
    #     search_fields = ['name']
    #     mapping = {
    #         'name': {'name': 'name', 'type': 'text', 'match': True},
    #         'website_url': {'name': 'website_url', 'type': 'url', 'truncate': False, 'html': False},
    #     }
    #
    #     mapping['detail'] = {'name': 'appointment_duration_formatted', 'type': 'text', 'html': True}
    #     if options['displayDescription']:
    #         mapping['description'] = {'name': 'message_intro', 'type': 'text', 'html': True, 'truncate': True}
    #
    #     return {
    #         'base_domain': domain,
    #         'fetch_fields': [value['name'] for _, value in mapping.items()],
    #         'icon': 'fa-calendar',
    #         'mapping': mapping,
    #         'model': 'appointment.type',
    #         'requires_sudo': bool(invite_token),
    #         'search_fields': search_fields,
    #     }

    def action_share_invite(self):
        action = super().action_share_invite()
        if self.env.user.has_group('website.group_multi_website'):
            website_id = self.website_id
        else:
            website_id = self.env['website']
        action['context'].update({'default_website_id': website_id.id})
        return action


    def _get_booking_slots(self, timezone, filter_users=None, filter_resources=None, asked_capacity=1, reference_date=None, employee=None):
        """ Fetch available slots to book an booking
            This method now uses the base implementation which properly handles both
            user-based and resource-based booking types through slot_ids configuration.
            
            :param timezone: timezone string e.g.: 'Europe/Brussels' or 'Etc/GMT+1'
            :param filter_users: filter available slots for those users
            :param filter_resources: filter available slots for those resources  
            :param asked_capacity: the capacity the user want to book
            :param reference_date: starting datetime to fetch slots
            :param employee: legacy parameter for backward compatibility
            :returns: list of dicts (1 per month) containing available slots per day per week.
        """
        self.ensure_one()
        
        # Use the base implementation for slot generation and availability checking
        # This handles both user-based and resource-based booking types properly
        return super()._get_booking_slots(timezone, filter_users, filter_resources, asked_capacity, reference_date)

    def _get_paginated_booking_slots(self, timezone, employee=None, month=0):
        booking_slots = self._get_booking_slots(timezone, employee=employee)
        try:
            return [booking_slots[month], booking_slots[month + 1]]
        except IndexError:
            return []
