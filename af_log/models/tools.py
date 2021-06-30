#  Copyright (c) 2021 Arbetsförmedlingen.
from odoo.http import request


def _get_request_object():
    """ Fetch the current request object, if one exists. We often run
    this code in sudo, so self.env.user is not reliable, but the
    request object always has the actual user.
    """
    try:
        # Poke the bear
        request.env
        # It's alive!
        return request
    except Exception:
        # No request is available
        return


def recursive_default(du, dd):
    """Update default values in du from dd. Will recurse if values are
    dicts.
    :arg du: dict to update.
    :arg dd: default dict.
    """
    for k, v in dd.items():
        if k in du:
            if type(du[k]) == dict:
                recursive_default(du[k], v)
        else:
            du[k] = v


def recursive_update(du, dv):
    """Update values in du from dv. Will recurse if values are dicts.
    :arg du: dict to update.
    :arg dv: dict to update from.
    """
    for k, v in dv.items():
        if k in du and type(du[k]) == dict:
            recursive_update(du[k], v)
        else:
            du[k] = v