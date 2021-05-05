#  Copyright (c) 2021 Arbetsförmedlingen.

from odoo import netsvc
from odoo.tools import config
import os
import json
import threading

import logging
_logger = logging.getLogger(__name__)

APPLICATION_NAME = config.get('af_log_app_name', 'CRM')

class DBFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, style='%'):
        """ Override supplied formats to our desired formats. This feels
        cleaner than overriding the entire init_logger function."""
        # JSON datetime format (ISO 8601) with UTC timezone.
        datefmt = '%Y-%m-%dT%H:%M:%S.%03dZ'
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
        # Provide audit_log through parameter extra in the logging functions.
        # Example: _logger.warning('foo', extra={'audit_log': {...}})
        audit_log = record_data.get('audit_log')
        if audit_log:
            # This is an audit log.
            log_data = {
                '@timestamp': record_data.get('asctime'),
                'user': audit_log['user'],
                'event': audit_log['event'],
                'source': audit_log.get('source', {}),
                'application': {
                    'name': 'CRM',
                    'thread': record_data.get('pid'),
                    'class': record_data.get('name'),
                    #'version': ???,
                },
                'audit': audit_log['audit'],
            }
        else:
            # This is an ordinary log entry.
            log_data = {
                '@timestamp': record_data.get('asctime'),
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
