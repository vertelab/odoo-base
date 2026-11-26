# -*- coding: utf-8 -*-
from . import models


def post_init_hook(env):
    """Migrate the API key out of ``ir.config_parameter``.

    Older installations stored the key as a system parameter. Copy it to the
    environment file so enrichment keeps working, then remove the parameter:
    leaving a credential in the database after it has been moved is worse than
    never having moved it.
    """
    params = env['ir.config_parameter'].sudo()
    # 20.0 renamed get_param/set_param to get_str/set_str.
    old_key = params.get_str('partner_foretagssok.api_key', default='')
    if not old_key:
        return
    env['res.partner']._foretagsapi_migrate_secret(old_key)
    params.set_str('partner_foretagssok.api_key', '')
