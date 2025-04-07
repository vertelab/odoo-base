from odoo.addons.portal.controllers.portal import CustomerPortal


class CustomerPortalExtended(CustomerPortal):

    def _get_mandatory_fields(self):
        """ This method is there so that we can override the mandatory fields """
        mandatory_fields = super()._get_mandatory_fields()
        mandatory_fields.append("allow_email_marketing")
        return mandatory_fields


