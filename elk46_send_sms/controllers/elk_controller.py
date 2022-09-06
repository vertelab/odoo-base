import odoo.http as http
from odoo.http import request
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
        _logger.warning(f"hello {kwargs=}")
        return {'response': 'OK'}
