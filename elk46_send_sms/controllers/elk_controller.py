from urllib import response
import odoo.http as http
from odoo.http import request, Response
import logging

_logger = logging.getLogger(__name__)


class ElkController(http.Controller):

    @http.route('/sms', type='http', auth='none', csrf=False)
    def receive_elk_post(self, **kwargs):
        """'
        Process SMS message from service X as described here:
            LINK-PLACEHOLDER

        TODO: Enter name of service and link to doc.
        """
        _logger.warning(f"incoming POST from 46elks {kwargs=}")
        if kwargs:
            try:
                saved_sms_id = http.request.env['sms.sms'].sudo().search([('elk_sms_id', '=', kwargs['id'])])
                saved_sms_id.elk_sms_status = kwargs.get('status')

                sale_order = http.request.env[saved_sms_id.rec_model].sudo().browse(int(saved_sms_id.rec_id))
                if kwargs['status'] in ['delivered', 'sent']:
                    saved_sms_id.state = 'sent'
                    sale_order.message_post(
                        body=f"Message with body: {saved_sms_id.body}, to number: {saved_sms_id.number}, "
                             f"was successfully {kwargs.get('status')}.")
                else:
                    saved_sms_id.state = 'error'
                    sale_order.message_post(
                        body=f'Message with body: {saved_sms_id.body}, to number: {saved_sms_id.number}, '
                             f'failed to send.')
            except Exception as e:
                _logger.warning(e)

        return Response(status=200)
