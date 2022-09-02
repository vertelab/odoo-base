import odoo.http as http
from odoo.http import request
import logging

_logger = logging.getLogger("------dmitri-------")

class ElkController(http.Controller):
    
    @http.route('/sms', type='http', auth='public')
    def recieve_elk_post(self, **kwargs):
        _logger.warning(f"{kwargs=}")