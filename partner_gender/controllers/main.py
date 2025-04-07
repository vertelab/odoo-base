from odoo import fields as odoo_fields, http, tools, _, SUPERUSER_ID
from odoo.http import request, route
from odoo.exceptions import ValidationError, AccessError, MissingError, UserError, AccessDenied
from odoo.addons.portal.controllers.portal import CustomerPortal
from requests import post


class CustomerPortalInherit(CustomerPortal):
    SKS_MANDATORY_BILLING_FIELDS = [
        "name", "phone", "email", "street", "city", "country_id", "gender"]
    SKS_OPTIONAL_BILLING_FIELDS = [
        "zipcode", "state_id", "vat", "company_name", "gender_txt"]

    @route(['/my/account'], type='http', auth='user', website=True)
    def account(self, redirect=None, **post):
        self.MANDATORY_BILLING_FIELDS.extend([x for x in self.SKS_MANDATORY_BILLING_FIELDS if x not in self.MANDATORY_BILLING_FIELDS])
        self.OPTIONAL_BILLING_FIELDS.extend([x for x in self.SKS_OPTIONAL_BILLING_FIELDS if x not in self.OPTIONAL_BILLING_FIELDS])
        return super(CustomerPortalInherit, self).account(redirect, **post)

    def details_form_validate(self, data):
        self.MANDATORY_BILLING_FIELDS.extend([x for x in self.SKS_MANDATORY_BILLING_FIELDS if x not in self.MANDATORY_BILLING_FIELDS])
        self.OPTIONAL_BILLING_FIELDS.extend([x for x in self.SKS_OPTIONAL_BILLING_FIELDS if x not in self.OPTIONAL_BILLING_FIELDS])
        return super(CustomerPortalInherit, self).details_form_validate(data)
