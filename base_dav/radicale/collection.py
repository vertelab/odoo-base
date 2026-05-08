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
        date = self.odoo_collection.create_date or self.odoo_collection.write_date or time.strftime('%Y-%m-%d %H:%M:%S')
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
        if key is None:
            return {
                'tag': str(self.odoo_collection.tag or ''),
                'D:displayname': str(self.odoo_collection.display_name or self._path),
            }
        elif key == 'tag':
            return str(self.odoo_collection.tag or '')
        elif key == 'D:displayname':
            return str(self.odoo_collection.display_name or self._path)
        elif key == 'C:supported-calendar-component-set':
            return 'VTODO,VEVENT,VJOURNAL'
        elif key in ('C:calendar-home-set', 'D:principal-URL'):
            return None
        elif key == 'ICAL:calendar-color':
            return '#48c9f4'
        return None

    def get_all(self):
        for href in self.odoo_collection.dav_list(self, self._path_components):
            yield self.odoo_collection.dav_get(self, href)

    def get_multi(self, hrefs):
        for href in hrefs:
            yield href, self.odoo_collection.dav_get(self, href)

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
            for odoo_col in self.env['dav.collection'].search([]):
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
