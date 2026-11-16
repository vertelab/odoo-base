# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

"""Tests for organisation number / VAT normalisation and the canonical format."""

from odoo.tests.common import TransactionCase

from ..models.enrich_format import clean, empty, to_float, to_int


class TestNormalizeRegistry(TransactionCase):
    """One normaliser, one storage format — the point of the exercise."""

    def _norm(self, value):
        return self.env['res.partner']._enrich_normalize_registry(value)

    def test_dashed_input(self):
        self.assertEqual(self._norm('556000-1234'), ('5560001234', 'SE556000123401'))

    def test_plain_digits(self):
        self.assertEqual(self._norm('5560001234'), ('5560001234', 'SE556000123401'))

    def test_vat_input(self):
        self.assertEqual(self._norm('SE556000123401'), ('5560001234', 'SE556000123401'))

    def test_spaced_vat_input(self):
        self.assertEqual(
            self._norm('SE 556000 1234 01'),
            ('5560001234', 'SE556000123401'),
        )

    def test_lowercase_vat_prefix(self):
        self.assertEqual(self._norm('se5560001234'), ('5560001234', 'SE556000123401'))

    def test_non_breaking_spaces(self):
        # Scraped values carry \xa0 between digit groups.
        self.assertEqual(
            self._norm('556000\xa01234'),
            ('5560001234', 'SE556000123401'),
        )

    def test_garbage_returns_false(self):
        for value in ('', None, False, 'abc', '12345', '556000123456789'):
            with self.subTest(value=value):
                self.assertEqual(self._norm(value), (False, False))

    def test_twelve_digits_not_vat_is_rejected(self):
        # Not a SE-prefixed VAT number, so it is not ours to interpret.
        self.assertEqual(self._norm('155600012340'), (False, False))

    def test_orgnr2vat_wrapper_delegates(self):
        partner = self.env['res.partner']
        self.assertEqual(partner.orgnr2vat('556000-1234'), 'SE556000123401')
        self.assertFalse(partner.orgnr2vat('nonsense'))

    def test_orgnr2vat_empty_returns_none(self):
        # Historical contract: None, not False, for an empty value.
        self.assertIsNone(self.env['res.partner'].orgnr2vat(False))


class TestCanonicalFormat(TransactionCase):
    """The format helpers, tested without any provider installed."""

    def test_empty_detects_missing_but_not_zero(self):
        self.assertTrue(empty(None))
        self.assertTrue(empty(''))
        self.assertTrue(empty([]))
        self.assertTrue(empty({}))
        self.assertFalse(empty(0))
        self.assertFalse(empty(0.0))
        self.assertFalse(empty('0'))

    def test_clean_drops_empty_values(self):
        data = {'name': 'Test AB', 'city': '', 'zip': None, 'phone': False}
        self.assertEqual(clean(data), {'name': 'Test AB'})

    def test_clean_strips_whitespace(self):
        self.assertEqual(clean({'city': '  Lund  '}), {'city': 'Lund'})

    def test_clean_drops_whitespace_only_strings(self):
        self.assertEqual(clean({'city': '   '}), {})

    def test_clean_drops_unknown_keys(self):
        # An unknown key must not reach write(); it is a provider bug.
        self.assertEqual(clean({'name': 'Test AB', 'totally_made_up': 'x'}), {'name': 'Test AB'})

    def test_clean_keeps_zero(self):
        # A financial figure of zero is data, not absence of data. Financial
        # keys belong to the ``financials`` sub-dict, so zero must survive
        # there and not be filtered out on the way.
        self.assertEqual(
            clean({'financials': [{'fiscal_year': 2025, 'net_sales': 0}]}),
            {'financials': [{'fiscal_year': 2025, 'net_sales': 0}]},
        )

    def test_clean_empty_input(self):
        self.assertEqual(clean(None), {})
        self.assertEqual(clean({}), {})

    def test_to_int(self):
        self.assertEqual(to_int('12'), 12)
        self.assertEqual(to_int('12.0'), 12)
        self.assertEqual(to_int('  12 '), 12)
        self.assertFalse(to_int(''))
        self.assertFalse(to_int('abc'))

    def test_to_float_swedish_decimal_comma(self):
        self.assertEqual(to_float('1 234,50'), 1234.5)
        self.assertEqual(to_float('1234,50'), 1234.5)

    def test_to_float_thousand_separator(self):
        self.assertEqual(to_float('1 234 567'), 1234567.0)

    def test_to_float_dot_decimal(self):
        self.assertEqual(to_float('1234.50'), 1234.5)

    def test_to_float_negative(self):
        self.assertEqual(to_float('-500'), -500.0)

    def test_to_float_numeric_passthrough(self):
        self.assertEqual(to_float(42), 42.0)

    def test_to_float_empty(self):
        self.assertFalse(to_float(''))
        self.assertFalse(to_float(None))
