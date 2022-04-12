from odoo import fields as odoo_fields, http, tools, _, SUPERUSER_ID
from odoo.http import request
from odoo.exceptions import ValidationError, AccessError, MissingError, UserError, AccessDenied
from odoo.addons.portal.controllers.portal import CustomerPortal

class CustomerPortalInherit(CustomerPortal):
    SKS_MANDATORY_BILLING_FIELDS = ["name", "phone", "email", "street", "city", "country_id", "gender"]
    SKS_OPTIONAL_BILLING_FIELDS = ["zipcode", "state_id", "vat", "company_name", "gender_txt"]

    def details_form_validate(self, data):
        error = dict()
        error_message = []

        # Validation
        for field_name in self.SKS_MANDATORY_BILLING_FIELDS:
            if not data.get(field_name):
                error[field_name] = 'missing'

        # email validation
        if data.get('email') and not tools.single_email_re.match(data.get('email')):
            error["email"] = 'error'
            error_message.append(_('Invalid Email! Please enter a valid email address.'))

        # vat validation
        partner = request.env.user.partner_id
        if data.get("vat") and partner and partner.vat != data.get("vat"):
            if partner.can_edit_vat():
                if hasattr(partner, "check_vat"):
                    if data.get("country_id"):
                        data["vat"] = request.env["res.partner"].fix_eu_vat_number(int(data.get("country_id")), data.get("vat"))
                    partner_dummy = partner.new({
                        'vat': data['vat'],
                        'country_id': (int(data['country_id'])
                                       if data.get('country_id') else False),
                    })
                    try:
                        partner_dummy.check_vat()
                    except ValidationError:
                        error["vat"] = 'error'
            else:
                error_message.append(_('Changing VAT number is not allowed once document(s) have been issued for your account. Please contact us directly for this operation.'))

        # error message for empty required fields
        if [err for err in error.values() if err == 'missing']:
            error_message.append(_('Some required fields are empty.'))

        unknown = [k for k in data if k not in self.SKS_MANDATORY_BILLING_FIELDS + self.SKS_OPTIONAL_BILLING_FIELDS]
        if unknown:
            error['common'] = 'Unknown field'
            error_message.append("Unknown field '%s'" % ','.join(unknown))

        return error, error_message