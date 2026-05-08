# Copyright 2018 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging
from odoo.http import request

try:
    from radicale.rights import BaseRights
except ImportError:
    BaseRights = object

logger = logging.getLogger(__name__)


class Rights(BaseRights):

    def __init__(self, configuration):
        super().__init__(configuration)

    def authorization(self, user, path):
        if path == '/':
            return "R"

        components = [c for c in path.strip('/').split('/') if c]

        # Principal path /username — allow authenticated users to discover
        if len(components) == 1:
            return "R" if user else ""

        if len(components) < 2 or not components[1].isdigit():
            return ""

        odoo_collection = request.env['dav.collection'].sudo().browse(
            int(components[1])
        )

        if not odoo_collection.exists():
            return ""

        rights = odoo_collection.rights
        owner_login = odoo_collection.create_uid.login

        if rights == 'authenticated':
            return "RW" if user else ""

        elif rights == 'owner_write_only':
            if not user:
                return "R"
            return "RW" if owner_login == user else "R"

        elif rights == 'owner_only':
            if not user:
                return ""
            return "RW" if owner_login == user else ""

        return ""
