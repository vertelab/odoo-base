#  Copyright (c) 2021 Arbetsförmedlingen.

from odoo import models, api

import logging
_logger = logging.getLogger(__name__)


class Users(models.Model):
    _inherit = 'res.users'

    @api.multi
    def _af_log_record(self) -> dict:
        """ Generate a user record for the log."""
        return {
            'name': self.login  # Personnummer or signature
            # 'initiatinguser': Personnummer or signature. Supplied by the user.
            #                   Another user initiated this event.
        }
