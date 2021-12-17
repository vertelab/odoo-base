# -*- coding: utf-8 -*-
#############################################################################
#
#    BizzAppDev
#    Copyright (C) 2004-TODAY bizzappdev(<http://www.bizzappdev.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

import logging

from odoo.models import AbstractModel
from odoo import api
from odoo.release import version_info
from odoo.tools.config import config

config['publisher_warranty_url'] = ''
_logger = logging.getLogger(__name__)


### TODO: Remove this, this is only here to keep a record of all POST requests
import requests

good_post = requests.post
def my_post(*args, **kwargs):
    _logger.info("ANY POST:\n args: %s\n kwargs: %s", str(args), str(kwargs))
    return good_post(*args, **kwargs)

requests.post = my_post
### TODO: Remove this


class PublisherWarrantyContract(AbstractModel):
    _inherit = "publisher_warranty.contract"

    def __init__(self, *args, **kwargs):
        _logger.info("base_no_call_home: Created instance")
        super(PublisherWarrantyContract, self).__init__(*args, **kwargs)

    @api.model
    def _get_message(self):
        _logger.info("base_no_call_home: _get_message")
        if version_info and isinstance(version_info, (list,tuple)) and 'e' == version_info[-1]:
            ret = super(PublisherWarrantyContract, self)._get_message()
            return ret
        return {}

    @api.model
    def _get_sys_logs(self):
        _logger.info("base_no_call_home: _get_sys_logs")
        if version_info and isinstance(version_info, (list,tuple)) and 'e' == version_info[-1]:
            ret = super(PublisherWarrantyContract, self)._get_sys_logs()
            return ret
        return

    def update_notification(self, cron_mode=True):
        _logger.info("base_no_call_home: update_notification")
        if version_info and isinstance(version_info, (list, tuple)) and 'e' == version_info[-1]:
            return super(PublisherWarrantyContract, self).update_notification(cron_mode=cron_mode)
        _logger.info("base_no_call_home: No more phoning Home Stuff")
        return True

    @api.model
    def set_notification_update(self, cron_id):
        _logger.info("base_no_call_home: set_notification_update")
        if version_info and isinstance(version_info, (list,tuple)) and 'e' == version_info[-1]:
            self.env['ir.cron'].browse(cron_id).write({'active': True})
        else:
            self.env['ir.cron'].browse(cron_id).write({'active': False})

PublisherWarrantyContract()
