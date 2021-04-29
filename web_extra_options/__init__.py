from odoo import models, api

import logging
_logger = logging.getLogger(__name__)

class Partner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def test_log_stuff(self):
        return _logger
