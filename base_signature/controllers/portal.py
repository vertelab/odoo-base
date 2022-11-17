
import binascii

from odoo import fields, http, SUPERUSER_ID, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.payment.controllers.portal import PaymentProcessing
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from odoo.osv import expression


class SignaturePortal(CustomerPortal):

    @http.route(['/web/signature/<string:model>/<int:rec_id>/accept'], type='json', auth="public", website=True)
    def portal_signature_accept(self, model, rec_id, access_token=None, name=None, signature=None):
        # get from query string if not on json param
        access_token = access_token or request.httprequest.args.get('access_token')
        try:
            rec_sudo = self._document_check_access(model, int(rec_id), access_token=access_token)
        except (AccessError, MissingError):
            return {'error': _('Invalid order.')}

        if not rec_sudo.require_signature:
            return {'error': _('The record does not require signature.')}
        if not signature:
            return {'error': _('Signature is missing.')}

        try:
            rec_sudo.write({
                'signed_date': fields.Datetime.now(),
                'signature': signature,
            })
            request.env.cr.commit()
        except (TypeError, binascii.Error) as e:
            return {'error': _('Invalid signature data.')}

        _message_post_helper(
            model, rec_sudo.id, _('Signed by %s') % (name,),
            attachments=False,
            **({'token': access_token} if access_token else {}))

        query_string = 'message=sign_ok'

        return {
            'force_refresh': True,
            'redirect_url': '/my/dms/file/%s?%s' % (rec_sudo.id, query_string),
        }

