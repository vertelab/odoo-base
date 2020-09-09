# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution, third party addon
#    Copyright (C) 2020 Vertel AB (<http://vertel.se>).
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

import odoo.service.db
from time import sleep

_create_empty_database = odoo.service.db._create_empty_database

def _create_empty_database_sleep(name):
    res = _create_empty_database(name)
    # We try to connect to the new database too fast for pgpool.
    # If we get sent to a standby node the db has not been synced yet.
    # A 3 second wait should be more than enough to complete the sync.
    sleep(3)
    return res

# Monkey patching our function into core.
odoo.service.db._create_empty_database = _create_empty_database_sleep

# TODO: Look into issues when deleting a database.
