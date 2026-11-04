# Copyright 2019-2020 initOS GmbH <https://initos.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from datetime import datetime, timedelta
from unittest import mock

from odoo.tests.common import TransactionCase
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

from ..radicale.collection import Collection, Storage


class TestCalendar(TransactionCase):
    def setUp(self):
        super().setUp()

        self.collection = self.env["dav.collection"].create({
            "name": "Test Collection",
            "dav_type": "calendar",
            "model_id": self.env.ref("base.model_res_users").id,
            "domain": "[]",
        })

        self.create_field_mapping(
            "login", "login",
            excode="result = record.login",
            imcode="result = item.value",
        )
        self.create_field_mapping("name", "name")
        self.create_field_mapping("dtstart", "create_date")
        self.create_field_mapping("dtend", "write_date")

        start = datetime.now()
        stop = start + timedelta(hours=1)
        # account declares res.partner.autopost_bills as required without a DB
        # default. base_dav only depends on base, so when this test runs the
        # field may be unloaded and the ORM never fills the column. Writing it
        # with SQL afterwards is not possible either (NOT NULL), so create the
        # partner through the ORM with the column pre-set via a savepoint-free
        # helper below.
        partner = self._create_partner("Test User")
        self._ensure_not_null_defaults()
        self.record = self.env["res.users"].create({
            "login": "tester",
            "name": "Test User",
            "partner_id": partner.id,
            "create_date": start.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
            "write_date": stop.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
        })

    # NOT NULL columns whose Python default lives in a module that base_dav
    # does not depend on (account, mail, calendar). Without a DB default the
    # INSERT omits them and PostgreSQL rejects the row.
    _NOT_NULL_DEFAULTS = {
        "res_partner": {"autopost_bills": "'ask'"},
        "res_users": {
            "notification_type": "'email'",
            "apps_menu_search_type": "'bar'",
            "apps_menu_theme": "'default'",
        },
        "res_users_settings": {"calendar_default_privacy": "'public'"},
    }

    def _ensure_not_null_defaults(self):
        for table, columns in self._NOT_NULL_DEFAULTS.items():
            for column, default in columns.items():
                self.env.cr.execute(
                    f'ALTER TABLE "{table}" ALTER COLUMN "{column}" '
                    f"SET DEFAULT {default}"
                )

    def _create_partner(self, name):
        """Create a res.partner, tolerating the required autopost_bills column.

        account marks res.partner.autopost_bills required=True with a Python
        default, but base_dav does not depend on account. When account is not
        loaded the ORM does not know the field and the INSERT omits the
        NOT NULL column. Fill it with SQL before the ORM flush.
        """
        self._ensure_not_null_defaults()
        return self.env["res.partner"].create({"name": name})

    def _field_id(self, field_name):
        """Look up ir.model.fields directly.

        Odoo does not create ir.model.data xmlids for base fields such as
        res.users.login, so env.ref("base.field_res_users_login") raises
        KeyError.
        """
        return self.env["ir.model.fields"]._get("res.users", field_name).id

    def create_field_mapping(self, name, field_name, imcode=None, excode=None):
        return self.env["dav.collection.field_mapping"].create({
            "collection_id": self.collection.id,
            "name": name,
            "field_id": self._field_id(field_name),
            "mapping_type": "code" if imcode or excode else "simple",
            "import_code": imcode,
            "export_code": excode,
        })

    def compare_record(self, vobj, rec=None):
        tmp = self.collection.from_vobject(vobj)
        rec = rec or self.record

        self.assertEqual(rec.login, tmp["login"])
        self.assertEqual(rec.name, tmp["name"])
        # Datetime fields come back from from_vobject() as the strings that go
        # into the ORM, not as datetime objects.
        self.assertEqual(
            rec.create_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
            tmp["create_date"],
        )
        self.assertEqual(
            rec.write_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
            tmp["write_date"],
        )

    def test_import_export(self):
        # Exporting and importing should result in the same record
        vobj = self.collection.to_vobject(self.record)
        self.compare_record(vobj)

    def test_get_record(self):
        rec = self.collection.get_record([self.record.id])
        self.assertEqual(rec, self.record)

        self.collection.field_uuid = self._field_id("login")
        rec = self.collection.get_record([self.record.login])
        self.assertEqual(rec, self.record)

    def test_collection(self):
        # odoo.http.request is a werkzeug LocalProxy, so mock.patch() tries to
        # read it while unbound and raises RuntimeError. Patch the module
        # attribute through a plain object instead.
        request_mock = mock.MagicMock()
        request_mock.env = self.env
        patcher = mock.patch(
            "odoo.addons.base_dav.radicale.collection.request", request_mock
        )
        patcher.start()
        self.addCleanup(patcher.stop)
        collection_url = "/%s/%s" % (self.env.user.login, self.collection.id)
        # base_dav implements the Radicale 3.x Storage API: discover() lives on
        # Storage and a Collection exposes get_all()/get_multi()/upload()/
        # delete() instead of the 2.x list()/get().
        storage = Storage(None)
        collection = list(storage.discover(collection_url))[0]

        # The collection lists the record. get_all() yields hrefs relative to
        # the collection, so compare against the bare record id.
        record_url = "%s/%s" % (collection_url, self.record.id)
        hrefs = [item.href for item in collection.get_all()]
        self.assertIn(str(self.record.id), hrefs)

        # Get the record using the URL and compare it
        item = next(iter(collection.get_multi([record_url])))[1]
        self.compare_record(item.vobject_item)
        self.assertEqual(item.href, record_url)

        # Get the record and alter it later
        vobj = self.collection.to_vobject(self.record)
        self.record.login = "different"
        with self.assertRaises(AssertionError):
            self.compare_record(vobj)

        # Restore the record. upload() expects the vobject itself, not the
        # radicale Item wrapper.
        item, _ = collection.upload(record_url, item.vobject_item)
        self.compare_record(item.vobject_item)

        # Delete the record
        collection.delete(item.href)
        self.assertFalse(self.record.exists())

        # Create a new record
        item, _ = collection.upload(record_url + "0", item.vobject_item)
        record = self.collection.get_record(collection._split_path(item.href))
        self.assertNotEqual(record, self.record)
        self.compare_record(item.vobject_item, record)
