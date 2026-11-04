# Copyright 2018 Therp BV <https://therp.nl>
# Copyright 2019-2020 initOS GmbH <https://initos.com>
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

    @staticmethod
    def _is_granted(user, odoo_collection, owner_login):
        """Is this collection available to the authenticated user?

        Ownership alone is not enough. A collection seeded by a data file is
        created by the system user, so its create_uid is not the person it is
        meant for: user_settings_dav ships a "User Calendar" collection whose
        domain selects each user's own events, yet create_uid is '__system__'.
        With rights='owner_only' that made the collection reachable by nobody,
        and clients got PROPFIND 401 on their own calendar even with correct
        credentials.

        user_settings_dav therefore exposes res.users.dav_collection_ids so an
        administrator can grant a collection explicitly. That field was
        written by the UI but never read here, so honour it as well.
        """
        if owner_login == user:
            return True
        granted = request.env['res.users'].sudo().search([
            ('login', '=', user),
            ('dav_collection_ids', 'in', odoo_collection.id),
        ], limit=1)
        return bool(granted)

    def authorization(self, user, path):
        if path == '/':
            return "Rr"

        components = [c for c in path.strip('/').split('/') if c]

        # Principal path /username — allow authenticated users to discover
        if len(components) == 1:
            return "Rr" if user else ""

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
            return "RWrw" if user else ""

        elif rights == 'owner_write_only':
            if not user:
                return "Rr"
            if self._is_granted(user, odoo_collection, owner_login):
                return "RWrw"
            return "Rr"

        elif rights == 'owner_only':
            if not user:
                return ""
            if self._is_granted(user, odoo_collection, owner_login):
                return "RWrw"
            return ""

        return ""
