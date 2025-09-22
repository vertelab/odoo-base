from odoo.addons.portal.controllers.portal import CustomerPortal


class CustomerPortalExtended(CustomerPortal):

    # def _get_mandatory_fields(self):
    def _get_optional_fields(self):
        """ This method is there so that we can override the mandatory fields """
        optional_fields = super()._get_optional_fields()
        optional_fields.append("allow_email_marketing")
        return optional_fields


