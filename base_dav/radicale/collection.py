# Copyright 2018 Therp BV <https://therp.nl>
# Copyright 2019-2020 initOS GmbH <https://initos.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import base64
import os
import time
from contextlib import contextmanager

from odoo.http import request

try:
    from radicale.storage import BaseStorage, BaseCollection
    from radicale.item import Item
    import radicale.item as radicale_item
except ImportError:
    BaseStorage = object
    BaseCollection = object
    Item = object
    radicale_item = None


class BytesPretendingToBeString(bytes):
    def encode(self, encoding):
        return self


class FileItem:
    """Tricks radicale into serving a plain file (e.g. vCard attachment)."""

    def __init__(self, item, href, collection):
        self.item = item
        self.href = href
        self.collection = collection

    @property
    def name(self):
        return 'VCARD'

    def serialize(self):
        return BytesPretendingToBeString(base64.b64decode(self.item.datas or b''))

    @property
    def etag(self):
        datas = self.item.datas
        if not datas:
            return '"empty"'
        import hashlib
        return '"%s"' % hashlib.sha256(datas).hexdigest()[:16]


import logging

logger = logging.getLogger(__name__)

class Collection(BaseCollection):
    """Radicale 3.x BaseCollection implementation backed by Odoo dav.collection."""

    def __init__(self, path, odoo_collection=None):
        self._path = path.strip('/')
        self._path_components = self._split_path(path)
        self._odoo_collection = odoo_collection
        logger.info("Initialized Collection for path: %s", self._path)

    @staticmethod
    def _split_path(path):
        return list(filter(
            None, os.path.normpath(path or '').strip('/').split('/')
        ))

    @property
    def path(self):
        return self._path

    @property
    def env(self):
        return request.env

    @property
    def odoo_collection(self):
        if self._odoo_collection is not None:
            return self._odoo_collection
        if (len(self._path_components) >= 2 and
            str(self._path_components[1]).isdigit()):
            return self.env['dav.collection'].sudo().browse(
                int(self._path_components[1])
            )
        return None

    @property
    def last_modified(self):
        collection = self.odoo_collection
        if collection is None:
            date = time.strftime('%Y-%m-%d %H:%M:%S')
        else:
            date = (collection.create_date or collection.write_date
                    or time.strftime('%Y-%m-%d %H:%M:%S'))
        return self._odoo_to_http_datetime(date)

    def _odoo_to_http_datetime(self, value):
        try:
            value = str(value).split('.')[0]
            return time.strftime(
                '%a, %d %b %Y %H:%M:%S GMT',
                time.strptime(value, '%Y-%m-%d %H:%M:%S'),
            )
        except Exception:
            logger.error("Failed to parse datetime: %s", value)
            return time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime())

    def get_meta(self, key=None):
        logger.info("get_meta called for key: %s on path: %s", key, self._path)
        # The root path ('/') and the principal path ('/<login>') have no
        # backing dav.collection record: they exist so clients can discover
        # the user's collections. rights.py already grants "Rr" on both, and
        # Storage.discover() yields a Collection for them, so get_meta() must
        # answer as a plain collection instead of dereferencing None. Before
        # this guard a client's very first PROPFIND (/.well-known/caldav ->
        # /.dav) raised AttributeError: 'NoneType' object has no attribute
        # 'tag' -> HTTP 500, which DAVx5 reports as "Couldn't find CalDAV or
        # CardDAV service" even though OPTIONS and the leaf paths worked.
        collection = self.odoo_collection
        if collection is None:
            if key is None:
                return {
                    'tag': '',
                    'D:displayname': str(self._path or '/'),
                }
            if key == 'D:displayname':
                return str(self._path or '/')
            if key == 'C:supported-calendar-component-set':
                return 'VTODO,VEVENT,VJOURNAL'
            if key == 'ICAL:calendar-color':
                return '#48c9f4'
            return None
        if key is None:
            return {
                'tag': str(collection.tag or ''),
                'D:displayname': str(collection.display_name or self._path),
            }
        elif key == 'tag':
            return str(collection.tag or '')
        elif key == 'D:displayname':
            return str(collection.display_name or self._path)
        elif key == 'C:supported-calendar-component-set':
            return 'VTODO,VEVENT,VJOURNAL'
        elif key in ('C:calendar-home-set', 'D:principal-URL'):
            return None
        elif key == 'ICAL:calendar-color':
            return '#48c9f4'
        return None

    def get_all(self):
        # A principal/root collection has no backing record and therefore no
        # items of its own; its children are produced by Storage.discover().
        collection = self.odoo_collection
        if collection is None:
            return
        for href in collection.dav_list(self, self._path_components):
            yield collection.dav_get(self, href)

    def get_multi(self, hrefs):
        collection = self.odoo_collection
        if collection is None:
            return
        for href in hrefs:
            yield href, collection.dav_get(self, href)

    def upload(self, href, item):
        result = self.odoo_collection.dav_upload(self, href, item)
        return result, None

    def delete(self, href=None):
        self.odoo_collection.dav_delete(self, self._split_path(href) if href else [])


class Storage(BaseStorage):
    """Radicale 3.x Storage entry point — replaces the old Collection.discover()."""

    def __init__(self, configuration):
        super().__init__(configuration)

    @property
    def env(self):
        return request.env

    @staticmethod
    def _split_path(path):
        return list(filter(
            None, os.path.normpath(path or '').strip('/').split('/')
        ))

    def discover(self, path, depth='0', child_context_manager=None, user_groups=set()):
        depth = int(depth or '0')
        components = self._split_path(path)
        collection = Collection(path)

        if len(components) > 2:
            if collection.odoo_collection.dav_type == 'files' and depth:
                for item in collection.get_all():
                    yield item
                return
            yield collection.odoo_collection.dav_get(collection, path)
            return

        yield collection

        if depth and len(components) == 1:
            # .sudo() is required: Radicale authenticates through its own auth
            # class, not through an Odoo session, so request.env.user is an
            # empty recordset here. A plain search([]) then hits
            # ir.model.access.check -> _get_group_ids -> ensure_one(), which
            # raises "ValueError: Expected singleton: res.users()" and turns
            # every PROPFIND on the principal path into a 500.
            #
            # Access is not weakened by this: rights.py still authorizes each
            # collection individually (owner_only / owner_write_only /
            # authenticated) on every request, and discover() only advertises
            # the collections the client may then actually read.
            for odoo_col in self.env['dav.collection'].sudo().search([]):
                yield Collection(
                    '/'.join(components + [str(odoo_col.id)]),
                    odoo_collection=odoo_col,
                )

        if depth and len(components) == 2:
            for item in collection.get_all():
                yield item

    @contextmanager
    def acquire_lock(self, mode, user='', *args, **kwargs):
        """Odoo's database handles locking."""
        yield

    def move(self, item, to_collection, to_href):
        raise NotImplementedError

    def create_collection(self, href, items=None, props=None):
        raise NotImplementedError

    def verify(self):
        return True
