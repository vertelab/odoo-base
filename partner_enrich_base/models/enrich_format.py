# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

"""The canonical enrichment format.

Every provider module returns a dict shaped by these field groups. The groups
are the contract — not the individual fields. A provider may only write keys
that exist here; anything else is a programming error and is logged.

Design note: a key whose value is empty is *omitted*, never set to ``None`` or
``False``. That distinction is what keeps an enrichment run from clearing a
field the user has filled in by hand (see ``partner-allabolag``'s
``_set_company_details()``, which wrote ``name: None``).
"""

import logging

_logger = logging.getLogger(__name__)

#: The field groups. Order matters only for display; policy is per group.
CANONICAL_GROUPS = (
    'identity',
    'address',
    'contact',
    'classification',
    'financials',
    'media',
    'raw',
)

#: Every key a provider may return, grouped by field group.
CANONICAL_FIELDS = {
    'identity': (
        'name',
        'company_registry',   # stored as ten digits, no separators
        'vat',                # stored as SE + ten digits + 01
        'legal_form',
        'status',
        'registration_date',
    ),
    'address': (
        'street',
        'street2',
        'zip',
        'city',
        'country_code',
    ),
    'contact': (
        'phone',
        'mobile',
        'email',
        'website',
    ),
    'classification': (
        'sni_codes',          # list of SNI code strings
        'industry_code',
    ),
    'financials': (
        'financials',         # list of dicts, see FINANCIAL_FIELDS
    ),
    'media': (
        'logo',               # base64
    ),
    'raw': (
        'provider',
        'fetched_at',
        'payload',
    ),
}

#: Keys allowed inside each ``financials`` entry.
FINANCIAL_FIELDS = (
    'fiscal_year',
    'fiscal_year_start',
    'fiscal_year_end',
    'net_sales',
    'operating_profit',
    'net_result',
    'result_after_financial_items',
    'profit_before_tax',
    'total_assets',
    'equity',
    'current_assets',
    'current_liabilities',
    'cash_and_bank',
    'long_term_liabilities',
    'fixed_assets',
    'restricted_equity',
    'unrestricted_equity',
    'untaxed_reserves',
    'proposed_dividend',
    'employees',
    'solidity',
    'operating_margin',
    'taxonomy',
    'currency',
)

#: Map canonical key -> Odoo field name on res.partner.
#:
#: Only keys that exist on a stock Odoo 18 database are listed. Fields added by
#: other enrichment modules (``foretagssok_*``, ``bw_*``, ``mining_*``) are
#: mapped by those modules through ``_enrich_apply_extra()`` — putting them here
#: would make this base module fail to load without its providers.
PARTNER_FIELD_MAP = {
    'name': 'name',
    'company_registry': 'company_registry',
    'vat': 'vat',
    'street': 'street',
    'street2': 'street2',
    'zip': 'zip',
    'city': 'city',
    'country_code': 'country_id',
    'phone': 'phone',
    'mobile': 'mobile',
    'email': 'email',
    'website': 'website',
    'logo': 'image_1920',
}

#: Map canonical key -> Odoo field name on crm.lead.
#:
#: ``partner_name`` rather than ``name``: the lead's own ``name`` is the
#: opportunity title and must never be overwritten by a company name.
LEAD_FIELD_MAP = {
    'name': 'partner_name',
    'company_registry': 'company_registry',
    'vat': 'vat',
    'street': 'street',
    'street2': 'street2',
    'zip': 'zip',
    'city': 'city',
    'country_code': 'country_id',
    'phone': 'phone',
    'mobile': 'mobile',
    'email': 'email_from',
    'website': 'website',
}

#: Group a key belongs to, computed once.
FIELD_GROUP = {
    key: group
    for group, keys in CANONICAL_FIELDS.items()
    for key in keys
}


def empty(value):
    """True when a provider value carries no information.

    ``False`` counts as empty: providers and Odoo both use it for "no value",
    and writing ``False`` over a manually entered field is exactly the bug this
    contract exists to prevent. ``0`` and ``0.0`` are *not* empty — a financial
    figure of zero is data.
    """
    if value is None or value is False:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, (list, tuple, dict, set)):
        return len(value) == 0
    return False


def clean(data):
    """Drop empty values and unknown keys from a provider dict.

    Unknown keys are logged rather than silently discarded: a typo in a
    provider map is otherwise invisible until someone notices a field that is
    always blank.
    """
    if not data:
        return {}
    result = {}
    for key, value in data.items():
        if key not in FIELD_GROUP:
            _logger.warning(
                "Enrichment provider returned unknown key %r — ignored. "
                "Known keys: %s",
                key, ', '.join(sorted(FIELD_GROUP)),
            )
            continue
        if empty(value):
            continue
        if isinstance(value, str):
            value = value.strip()
            if not value:
                continue
        result[key] = value
    return result


# ---------------------------------------------------------------------------
# Small helpers shared by the provider lookup code
# ---------------------------------------------------------------------------

def pick(mapping, *keys, default=False):
    """Return the first non-empty value among ``keys`` in ``mapping``.

    Providers differ in casing and nesting; this keeps the mapping functions
    from turning into ``or``-chains that read like a riddle.
    """
    for key in keys:
        value = mapping.get(key)
        if not empty(value):
            return value
    return default


def to_int(value):
    """Parse an integer out of a provider value, or ``False``."""
    if empty(value):
        return False
    try:
        return int(float(str(value).replace(' ', '').replace('\xa0', '')))
    except (ValueError, TypeError):
        return False


def to_float(value):
    """Parse a float out of a provider value, or ``False``.

    Handles Swedish decimal comma and non-breaking spaces used as thousand
    separators, both of which appear in scraped financial figures.
    """
    if empty(value):
        return False
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value)
    text = text.replace('\xa0', '').replace(' ', '')
    if ',' in text and '.' in text:
        text = text.replace('.', '').replace(',', '.')
    else:
        text = text.replace(',', '.')
    try:
        return float(text)
    except (ValueError, TypeError):
        return False
