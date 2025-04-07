from odoo import http
from odoo.addons.auth_signup.controllers.main import AuthSignupHome, SIGN_UP_REQUEST_PARAMS
from odoo.http import request

import logging

_logger = logging.getLogger(__name__)

SIGN_UP_REQUEST_PARAMS.update({'allow_email_marketing'})


class SignupExtended(AuthSignupHome):

    def do_signup(self, qcontext):
        # Capture allow_email_marketing field value

        # Call the original do_signup method to handle standard fields
        super(SignupExtended, self).do_signup(qcontext)

        # update the user-partner's allow_email_marketing field
        if user := request.env['res.users'].sudo().search([('login', '=', qcontext.get('login'))], limit=1):
            user.partner_id.sudo().write({'allow_email_marketing': qcontext.get('allow_email_marketing')})
