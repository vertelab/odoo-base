# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution, third party addon
#    Copyright (C) 2004-2021 Vertel AB (<http://vertel.se>).
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
##############################################################################

from odoo import models, fields, api
from datetime import datetime

class BaseLogin(models.Model):

    _name = 'base.login.reason'

    _rec_name = 'user_id'

    _description = "Base Login"

    user_id = fields.Many2one("res.users", "User")
    email = fields.Char("Login", related="user_id.email")
    login_reason = fields.Text("Login Reason")
    logged_in = fields.Datetime("Logged in")
    logged_out = fields.Datetime("Logged out")
    color = fields.Integer('Kanban Color Index')
    length = fields.Integer("Length")
    ticket_ID = fields.Char("Ticket ID")
    auditor_comment = fields.Text("Auditor comment")
    active_length = fields.Float("Active Length (Minutes)", compute="_count_active_time")
    session_ID = fields.Char("Session ID")
    state = fields.Selection([('logged_in','Logged In'), ('logged_out','Logged Out')], string="Status",
                             default="draft")
    status = fields.Selection([('draft','Sample'), ('audit','Audit'), ('failed','Failed'),('pass','Pass')],
                              string="Audit Status", default='draft')

    def _count_active_time(self):
        for login_base in self:
            if login_base.logged_in and login_base.logged_out:
                diff = login_base.logged_out - login_base.logged_in
                login_base.active_length = (diff.total_seconds())/60

