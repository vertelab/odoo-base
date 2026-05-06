# -*- coding: utf-8 -*-
from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    tic_identity_status = fields.Selection([
        ('verified','Verified'), ('unverified','Unverified')],
        string="Tic Identity", default='unverified', readonly=True, tracking=True)
    tic_identity_verified_date = fields.Datetime(string="Verified Date", readonly=True, tracking=True)

