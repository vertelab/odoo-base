# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

"""Logo as an enrichment provider.

Two things were wrong with this module before:

1. ``fetch_logo()`` was never called. No button, no cron, no server action —
   the method existed and nothing invoked it, so no logo was ever fetched by
   the module that exists to fetch logos.
2. It wrote ``image_1920`` directly, which meant it could never take part in a
   multi-provider run: whichever module ran last won, and there was no way to
   say "prefer this provider's logo".

It is now a provider like the others: it returns ``media.logo`` in the
canonical format and the base module decides whether to write it.
"""

import base64
import logging

from odoo import api, models

from odoo.addons.partner_enrich_base.models.enrich_format import empty

_logger = logging.getLogger(__name__)

#: The key this provider registers under in ``partner_enrich.provider_order``.
PROVIDER_KEY = 'logos'

#: A logo smaller than this is a tracking pixel or a spacer, not a logo.
MIN_LOGO_BYTES = 512

#: Never download more than this. A "logo" that is 40 MB is a photo.
MAX_LOGO_BYTES = 5 * 1024 * 1024


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # ---------------------------------------------------------------------
    # Provider contract
    # ---------------------------------------------------------------------

    @api.model
    def _enrich_from_provider(self, provider_key, ctx):
        """Answer the base module's provider call for ``logos``.

        Logos are never part of a *search*: a dropdown suggestion has no logo
        to show, and fetching one per keystroke would be absurd. Only the
        detail and enrich modes do work here.
        """
        if provider_key != PROVIDER_KEY:
            return super()._enrich_from_provider(provider_key, ctx)
        mode = ctx.get('mode') or 'enrich'
        if mode == 'search':
            return []
        try:
            record = ctx.get('record')
            website = ctx.get('website')
            if empty(website) and record is not None and record:
                website = record.website
            if empty(website):
                return {}
            logo = self._logos_fetch(website)
            if not logo:
                return {}
            return {
                'logo': logo,
                'payload': {'website': website},
            }
        except Exception:  # noqa: BLE001 - a scrape failure is not fatal
            _logger.warning(
                "Logo lookup failed for %r.", ctx.get('website'),
                exc_info=True,
            )
            return {}

    # ---------------------------------------------------------------------
    # Fetch
    # ---------------------------------------------------------------------

    @api.model
    def _logos_fetch(self, website):
        """Find and download a logo, returned as base64 or ``False``."""
        logo_url = self._logos_find_url(website)
        if not logo_url:
            return False
        return self._logos_download(logo_url)

    @api.model
    def _logos_find_url(self, website):
        """The URL of the most likely logo on a page, or ``False``.

        The strategies are ordered by confidence, not by convenience: a
        ``<link rel="icon">`` is a favicon (often 16×16), so it ranks below an
        ``<img>`` inside a ``logo`` container. Returning the favicon first is
        how you end up with a blurry 16-pixel square as the company logo.
        """
        from bs4 import BeautifulSoup
        from urllib.parse import urljoin

        import requests

        url = website.rstrip('/')
        try:
            response = requests.get(
                url,
                timeout=15,
                allow_redirects=True,
                headers={
                    'User-Agent': (
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                        'AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/122.0.0.0 Safari/537.36'
                    ),
                    'Accept': 'text/html,application/xhtml+xml,image/*,*/*;q=0.8',
                    'Accept-Language': 'sv-SE,sv;q=0.9,en;q=0.8',
                },
            )
            if response.status_code != 200:
                _logger.info("Logo: HTTP %s for %s", response.status_code, url)
                return False
            soup = BeautifulSoup(response.text, 'html.parser')
        except Exception:  # noqa: BLE001 - a broken site is not our problem
            _logger.info("Logo: could not read %s", url, exc_info=True)
            return False

        def first_img(selector):
            node = soup.select_one(selector)
            if not node:
                return False
            src = node.get('src') or node.get('data-src')
            return urljoin(url, src) if src else False

        def meta_content(attr, value):
            node = soup.find('meta', {attr: value})
            if not node:
                return False
            content = node.get('content')
            return urljoin(url, content) if content else False

        strategies = (
            lambda: first_img("img[src*='logo'], img[data-src*='logo']"),
            lambda: first_img('.logo img, #logo img, [class*="logo"] img'),
            lambda: first_img('header img, .header-logo img, [class*="header"] img'),
            lambda: meta_content('property', 'og:image'),
            lambda: meta_content('name', 'twitter:image'),
            lambda: first_img('.brand img, [class*="brand"] img'),
            lambda: first_img('nav img, .navbar img'),
            # Favicons last: they are usually 16–32 px.
            lambda: self._logos_link_href(soup, url, 'apple-touch-icon'),
            lambda: self._logos_link_href(soup, url, 'icon'),
        )
        for index, strategy in enumerate(strategies, 1):
            try:
                candidate = strategy()
            except Exception:  # noqa: BLE001 - one bad selector is not fatal
                continue
            if candidate:
                _logger.info("Logo: strategy %s found %s", index, candidate)
                return candidate
        _logger.info("Logo: nothing found on %s", url)
        return False

    @api.model
    def _logos_link_href(self, soup, base_url, rel):
        from urllib.parse import urljoin

        node = soup.find('link', {'rel': rel})
        if not node:
            return False
        href = node.get('href')
        return urljoin(base_url, href) if href else False

    @api.model
    def _logos_download(self, logo_url):
        """Download an image and return it base64-encoded, or ``False``."""
        import requests

        try:
            response = requests.get(logo_url, timeout=15, stream=True)
            if response.status_code != 200:
                _logger.info(
                    "Logo: HTTP %s for %s", response.status_code, logo_url,
                )
                return False
            content_type = response.headers.get('content-type', '')
            if content_type and not content_type.startswith('image/'):
                _logger.info(
                    "Logo: %s is %r, not an image.", logo_url, content_type,
                )
                return False
            content = response.content
        except Exception:  # noqa: BLE001
            _logger.info("Logo: download failed for %s", logo_url, exc_info=True)
            return False

        if len(content) < MIN_LOGO_BYTES:
            _logger.info(
                "Logo: %s is only %s bytes — treating it as a spacer.",
                logo_url, len(content),
            )
            return False
        if len(content) > MAX_LOGO_BYTES:
            _logger.info(
                "Logo: %s is %s bytes — too large to be a logo.",
                logo_url, len(content),
            )
            return False
        return base64.b64encode(content).decode('ascii')

    # ---------------------------------------------------------------------
    # Kept for callers outside the provider contract
    # ---------------------------------------------------------------------

    def find_logo_url(self):
        """The logo URL for this record, or ``None``.

        Kept as a public method because the original module exposed it and
        other code may call it directly. It now delegates to the provider
        implementation instead of carrying its own copy of the strategies.
        """
        self.ensure_one()
        if not self.website:
            return None
        return self._logos_find_url(self.website) or None

    def fetch_logo(self):
        """Fetch and store the logo for these records.

        This is the method the module always had — and which nothing ever
        called. It now goes through the enrichment pipeline, so the field-group
        policy applies: a logo the user uploaded by hand is not overwritten.
        """
        for record in self:
            if record.image_1920:
                continue
            record.partner_enrich()
        return True
