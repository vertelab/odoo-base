# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64
from unittest.mock import MagicMock, patch

from odoo.tests.common import TransactionCase

#: A 1×1 PNG, comfortably over the minimum size once padded.
PNG = base64.b64decode(
    'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8'
    'z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=='
)

HTML_WITH_LOGO = """
<html><head>
  <meta property="og:image" content="/social.png">
  <link rel="icon" href="/favicon.ico">
</head><body>
  <header><div class="site-logo"><img src="/img/logo.png" alt="Logo"></div></header>
</body></html>
"""

HTML_FAVICON_ONLY = """
<html><head><link rel="icon" href="/favicon.ico"></head><body></body></html>
"""


def _response(status=200, text='', content=b'', content_type='text/html'):
    mock = MagicMock()
    mock.status_code = status
    mock.text = text
    mock.content = content
    mock.headers = {'content-type': content_type}
    return mock


class LogosCase(TransactionCase):

    def setUp(self):
        super().setUp()
        self.partner_model = self.env['res.partner']
        self.partner = self.env['res.partner'].create({
            'name': 'Testbolaget AB',
            'website': 'https://testbolaget.se',
        })


class TestProviderContract(LogosCase):

    def test_other_provider_key_falls_through(self):
        self.assertFalse(
            self.partner_model._enrich_from_provider(
                'allabolag', {'mode': 'enrich'},
            ),
        )

    def test_search_mode_never_fetches(self):
        """A dropdown suggestion has no logo; fetching one per keystroke is absurd."""
        with patch(
            'odoo.addons.partner_get_logos.models.res_partner.ResPartner'
            '._logos_fetch',
        ) as fetch:
            result = self.partner_model._enrich_from_provider(
                'logos', {'mode': 'search', 'name': 'Test'},
            )
        self.assertEqual(result, [])
        fetch.assert_not_called()

    def test_no_website_gives_nothing(self):
        partner = self.env['res.partner'].create({'name': 'No site'})
        result = self.partner_model._enrich_from_provider(
            'logos', {'mode': 'enrich', 'record': partner, 'website': False},
        )
        self.assertEqual(result, {})

    def test_failure_returns_empty_not_raise(self):
        with patch(
            'odoo.addons.partner_get_logos.models.res_partner.ResPartner'
            '._logos_fetch',
            side_effect=RuntimeError('boom'),
        ):
            result = self.partner_model._enrich_from_provider(
                'logos', {'mode': 'enrich', 'website': 'https://x.se'},
            )
        self.assertEqual(result, {})

    def test_returns_canonical_logo_key(self):
        with patch(
            'odoo.addons.partner_get_logos.models.res_partner.ResPartner'
            '._logos_fetch',
            return_value='Zm9v',
        ):
            result = self.partner_model._enrich_from_provider(
                'logos', {'mode': 'enrich', 'website': 'https://x.se'},
            )
        self.assertEqual(result['logo'], 'Zm9v')


class TestFindUrl(LogosCase):

    def test_prefers_logo_image_over_favicon(self):
        """A 16-pixel favicon is not a company logo."""
        with patch('requests.get', return_value=_response(text=HTML_WITH_LOGO)):
            url = self.partner_model._logos_find_url('https://testbolaget.se')
        self.assertEqual(url, 'https://testbolaget.se/img/logo.png')

    def test_falls_back_to_favicon(self):
        with patch(
            'requests.get', return_value=_response(text=HTML_FAVICON_ONLY),
        ):
            url = self.partner_model._logos_find_url('https://testbolaget.se')
        self.assertEqual(url, 'https://testbolaget.se/favicon.ico')

    def test_non_200_gives_false(self):
        with patch('requests.get', return_value=_response(status=403)):
            self.assertFalse(
                self.partner_model._logos_find_url('https://testbolaget.se'),
            )

    def test_request_exception_gives_false(self):
        with patch('requests.get', side_effect=OSError('no route')):
            self.assertFalse(
                self.partner_model._logos_find_url('https://testbolaget.se'),
            )


class TestDownload(LogosCase):

    def test_accepts_a_real_image(self):
        payload = PNG + b'\x00' * 1024
        with patch(
            'requests.get',
            return_value=_response(content=payload, content_type='image/png'),
        ):
            result = self.partner_model._logos_download('https://x.se/logo.png')
        self.assertTrue(result)
        self.assertEqual(base64.b64decode(result), payload)

    def test_rejects_a_tiny_spacer(self):
        """A 70-byte image is a tracking pixel, not a logo."""
        with patch(
            'requests.get',
            return_value=_response(content=PNG, content_type='image/png'),
        ):
            self.assertFalse(
                self.partner_model._logos_download('https://x.se/logo.png'),
            )

    def test_rejects_a_non_image(self):
        with patch(
            'requests.get',
            return_value=_response(
                content=b'<html>' + b'x' * 5000, content_type='text/html',
            ),
        ):
            self.assertFalse(
                self.partner_model._logos_download('https://x.se/logo.png'),
            )

    def test_rejects_an_oversized_file(self):
        big = b'\x00' * (6 * 1024 * 1024)
        with patch(
            'requests.get',
            return_value=_response(content=big, content_type='image/png'),
        ):
            self.assertFalse(
                self.partner_model._logos_download('https://x.se/logo.png'),
            )

    def test_non_200_gives_false(self):
        with patch('requests.get', return_value=_response(status=404)):
            self.assertFalse(
                self.partner_model._logos_download('https://x.se/logo.png'),
            )


class TestFetchLogo(LogosCase):

    def test_fetch_logo_goes_through_the_pipeline(self):
        """The old method was never called by anything; now it enriches."""
        with patch.object(
            type(self.partner_model), 'partner_enrich',
        ) as enrich:
            self.partner.fetch_logo()
        enrich.assert_called_once()

    def test_existing_logo_is_not_refetched(self):
        # 20.0 wants BinaryValue (raw bytes) for a binary field; 18/19 take
        # the base64 string.
        try:
            from odoo.tools.binary import BinaryBytes
        except ImportError:
            BinaryBytes = None
        self.partner.image_1920 = (
            BinaryBytes(PNG) if BinaryBytes else base64.b64encode(PNG))
        with patch.object(
            type(self.partner_model), 'partner_enrich',
        ) as enrich:
            self.partner.fetch_logo()
        enrich.assert_not_called()

    def test_find_logo_url_without_website(self):
        partner = self.env['res.partner'].create({'name': 'No site'})
        self.assertIsNone(partner.find_logo_url())
