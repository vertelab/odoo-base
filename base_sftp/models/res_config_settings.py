# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    sftp_bind = fields.Char(string='Document_SFTP Bind', config_parameter='sftp_bind')
    sftp_host_key = fields.Char(string='Document_SFTP Host key', config_parameter='sftp_host_key')
