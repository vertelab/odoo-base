#  Copyright (c) 2021 Arbetsförmedlingen.

from odoo import netsvc
from odoo.tools import config
import os
import json
import threading

import logging
_logger = logging.getLogger(__name__)


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


APPLICATION_NAME = config.get('af_log_app_name', 'CRM')


class DBFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, style='%'):
        """ Override supplied formats to our desired formats. This feels
        cleaner than overriding the entire init_logger function."""
        # JSON datetime format (ISO 8601) with UTC timezone.
        datefmt = '%Y-%m-%dT%H:%M:%SZ'
        return super(DBFormatter, self).__init__(fmt=fmt, datefmt=datefmt, style=style)

    def format(self, record):
        """ Format log record into a string. We hijack this function to
        generate a JSON string."""
        record.pid = os.getpid()
        record.dbname = getattr(threading.current_thread(), 'dbname', '?')
        message = logging.Formatter.format(self, record)
        # Isolate the message part of the log message.
        message = message.split(': ', 1)[1]
        record_data = record.__dict__
        # Provide audit_log etc through parameter extra in the logging functions.
        # Example: _logger.warning('foo', extra={'json_log_data': {...}})
        json_log_data = record_data.get('json_log_data')
        if json_log_data:
            # This is a predefined log record, probably an audit log.
            log_data = json_log_data
            # Add timestamp and application info.
            recursive_default(
                log_data,
                {
                    '@timestamp': f"{record_data.get('asctime')}."
                                  "{record_data.get('msecs'):03.0f}Z",
                    'application': {
                        'name': 'CRM',
                        'thread': record_data.get('pid'),
                        'class': record_data.get('name'),
                    }
                })
        else:
            # This is an ordinary log entry.
            log_data = {
                '@timestamp': f"{record_data.get('asctime')}."
                              "{record_data.get('msecs'):03.0f}Z",
                'message': message,
                'application': {
                    'name': APPLICATION_NAME,
                    # 'version': '???' # TODO: Implement versioning in openshift images
                    'thread': record_data.get('pid'),
                    'class': record_data.get('name'),
                    #'version': ???,
                },
                'log': {
                    'level': record_data.get('levelname'),
                }
            }
        return json.dumps(log_data)


netsvc.DBFormatter = DBFormatter
