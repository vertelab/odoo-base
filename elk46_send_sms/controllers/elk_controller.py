from urllib import response
import odoo.http as http
from odoo.http import request, Response
import logging

_logger = logging.getLogger("------dmitri-------")

class ElkController(http.Controller):

    @http.route('/sms', type='http', auth='none', csrf=False)
    def recieve_elk_post(self, **kwargs):
        ''''
        Process SMS message from service X as described here:
            LINK-PLACEHOLDER

        TODO: Enter name of service and link to doc.
        '''
        _logger.warning(f"incoming POST from 46elks {kwargs=}")
        if kwargs:
            if kwargs['status'] != 'created' and kwargs['status'] != 'sent':
                try:
                    saved_sms_id = http.request.env['temp.elk.sms'].sudo().search([('elk_api_id', '=', kwargs['id'])])
                    saved_sms_record = saved_sms_id
                    saved_sms_record.status = kwargs['status']

                    sale_order = http.request.env['sale.order'].sudo().browse(saved_sms_record.sale_id)
                    if kwargs['status'] == 'delivered':
                        sale_order.message_post(body = f'Message with body: {saved_sms_record.body}, to number: {saved_sms_record.number}, was sucessfully sent.')
                    else:
                        sale_order.message_post(body = f'Message with body: {saved_sms_record.body}, to number: {saved_sms_record.number}, failed to send.')
                except Exception as e:

                     _logger.warning(e)

        return Response(status=200)

