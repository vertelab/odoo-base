#  Copyright (c) 2021 Arbetsförmedlingen.

from odoo import models, api
from odoo.exceptions import AccessError
from collections import OrderedDict
from copy import deepcopy
from .tools import recursive_default, recursive_update, _get_request_object
import logging
_logger = logging.getLogger(__name__)


class Users(models.Model):
    _inherit = 'res.users'

    @api.model
    def _af_audit_log_admin_human_readable_vals(self, values, write=False, model=None):
        """ Translate technical values to human readable format.
            :param values: The values to translate.
            :param write: True if values is write/create values.
        """
        # TODO: Implement the translation. How hard could it be?
        # TODO: The syntax differs between read and write/create values.
        #  Need more hr conversion methods...
        result = {}
        for k, v in values.items():
            # field_name: (HR field name, HR value)
            result[k] = (k, v)
        return result

    @api.model
    def _af_audit_log_admin_domain2search_terms(self, domain, model):
        # TODO: Implement domain translation to human readable format.
        return str(domain)

    @api.multi
    def _af_log_record(self) -> dict:
        """ Generate a user record for the log."""
        return {
            'name': self.login  # Personnummer or signature
            # 'initiatinguser': Personnummer or signature. Supplied by the user.
            #                   Another user initiated this event.
        }

    @api.multi
    def _af_audit_log_pre_admin_action(self, model, method, args, kwargs):
        """ Run before a method call made by admin.
        :arg model: The model of the method.
        :arg method: The method being called.
        :arg args: The arguments to the method.
        :arg kwargs: The keyword arguments to the method.
        :returns: Some data needed for audit log generation in
                  _af_audit_log_post_admin_action."""
        if method == 'write':
            # Save values before write
            ids = args[0]
            values = args[1]
            fields = [key for key in values]
            return {
                'values': model.search_read([('id', 'in', ids)], fields)
            }
        elif method == 'unlink':
            # Save values before unlink
            ids = args[0]
            return model.search_read([('id', 'in', ids)])

    @api.multi
    def _af_audit_log_post_admin_action(self, model, method, args, kwargs, res, before=None, error=None):
        """ Generate an admin audit log from a function call.
        :arg user: The user executing this method.
        :arg method: The method being called.
        :arg args: The arguments to the method.
        :arg kwargs: The keyword arguments to the method.
        :arg before: Data from _af_audit_log_pre_method, generated
                     before the method call.
        :arg res: The result of the method call.
        """
        if method == 'create':
            self._af_audit_log_admin_cruds(model, 'CREATE', values=args[0], result=res)
        elif method == 'read':
            pass
        elif method == 'write':
            self._af_audit_log_admin_cruds(model, 'UPDATE', ids=args[0], values=args[1], data=before, result=res)
        elif method == 'unlink':
            self._af_audit_log_admin_cruds(model, "DELETE", ids=args[0], values=before)
        elif method == 'search_read':
            pass
        else:
            # Generic method call
            request = _get_request_object()
            audit_log = {
                'user': self._af_log_record(),
                'event': {'action': method},
                'source': {'ip': request and request.httprequest.remote_addr or 'OKÄND'},
                'audit': {
                    'executioninfo': 1,
                    'objecttype': f"{model._description} ({model._name})",
                    'objectinfo': f"args: {args}, kwargs: {kwargs}",
                    'objectidtype': 'Databas-ID',
                    'objectid': 'OKÄND',
                }
            }
            # Check if first arg looks to be an id, or a list of ids
            if args and isinstance(args[0], list) and \
                    all([isinstance(i, int) for i in args[0]]):
                audit_log['audit'].update['objectid'] = ', '.join([str(i) for i in args[0]])
            elif args and isinstance(args[0], int):
                audit_log['audit'].update['objectid'] = str(args[0])
            if error:
                if isinstance(error, AccessError):
                    audit_log['audit']['authorisationinfo'] = 0
                else:
                    audit_log['audit']['executioninfo'] = 0
            _logger.warning('Audit log monkeypatch not installed.', extra={'json_log_data': audit_log})


    @api.multi
    def _af_audit_log_admin_cruds(self, model, operation, **kwargs):
        """ Generate an admin CRUDS audit log.
        :arg model: The Odoo model object.
        :arg operation:
        :arg operation: The operation. One of CREATE, UPDATE, or
        DELETE. READ, and SEARCH are not relevant in admin logs.
        :arg ids: The ids of the records affected by the operation.
        :arg data: Data from a read/search operation. Original data when
        writing. Use this instead of browse if possible.
        :arg search_terms: The search domain.
        :arg result: The result of a function call.
        :arg error: Error during execution.
        """
        log_objs = self._af_audit_log_admin_details(model, operation, **kwargs)
        if not log_objs:
            # Nothing to log
            return
        request = _get_request_object()
        audit_log = {
            'user': self._af_log_record(),
            'event': {'action': operation},
            'source': {'ip': request and request.httprequest.remote_addr or 'OKÄND'},
            'audit': {
                'executioninfo': 1,
            }
        }
        if kwargs.get('error'):
            if isinstance(kwargs.get('error'), AccessError):
                audit_log['audit']['authorisationinfo'] = 0
            else:
                audit_log['audit']['executioninfo'] = 0
        for obj in log_objs:
            log_record = deepcopy(audit_log)
            log_record['audit'].update({
                'objectid': obj['obj_id'],
                'objectidtype': obj['id_type'],
                'objecttype': obj['obj_type']})
            if operation == 'CREATE':
                info = [f'{k}={v}' for k, v in obj['values'].items()]
                log_record['audit']['objectinfo'] = info
            elif operation == 'READ':
                pass
            elif operation == 'UPDATE':
                info = [f'{v[0]}={v[1]}' for v in obj['values'].values()]
                log_record['audit']['objectinfo'] = info
            elif operation == 'DELETE':
                pass
            elif operation == 'SEARCH':
                pass
            recursive_default(log_record, obj.get('defaults', {}))
            recursive_update(log_record, obj.get('update', {}))
            _logger.warning('Audit log monkeypatch not installed.', extra={'json_log_data': log_record})

    @api.model
    def _af_audit_log_admin_details(self, model, operation, **kwargs):
        """ Must be implemented by inheriting models. Perform
        filtering of objects. Specify what type of log object it is,
        and any special log requirements. Convert internal values to
        human readable (HR) values.
        :returns: A list of log object descriptions.
        [{
            'obj_type': Arbetsförmedlingen HR internal name, e.g.
                        Arbetssökande, Arbetsgivare.
            'obj_id':   Arbetsförmedlingen HR object id, e.g. a
                        person or org number.
            'id_type':  The type of the id, e.g. Organisationsnummer or
                        Personnummer.
            'values':   {HR field name: HR field value},
            'defaults': Optional. dict with default values. Use to
                        implement special cases. Will be used to update
                        the audit records default values.
            'update':   Optional. dict with update values. Use to
                        implement special cases. Will be used to
                        overwrite the audit records values.
        }...]
        """
        log = []
        # if operation == 'CREATE':
        #     # values: create vals
        #     # result: create result ( so... True?)
        #     pass
        if operation == 'CREATE':
            # values: create values
            # result: create result ( so... recordset or id?)
            # Fetch create values
            values = kwargs.get('values', {})
            # Could be single or multi create. Handle everything as multi.
            if type(values) != list:
                values = [values]
            # Look up created records
            records = kwargs.get('result')
            if records:
                if type(records) != list:
                    records = [records]
                records = self.search_read([('id', 'in', records)])  # , setup['required_fields'])
            else:
                # Create empty dummy records
                records = [{} for x in range(len(values))]
            for record, value in zip(records, values):
                if 'name' in record:
                    obj_id = f"{record['name']} ({record['id']})"
                    id_type = "namn och databas-id"
                else:
                    obj_id = f"{record['id']}"
                    id_type = "databas-id"
                log.append({
                    'obj_type': f"{model._description} ({model._name})",
                    'obj_id': obj_id,
                    'id_type': id_type,
                    'values': self._af_audit_log_admin_human_readable_vals(values, model=model),
                })
        elif operation == 'READ':
            # ids: record ids
            # data: read from before update (_af_audit_log_pre_method)
            # result: read values
            data = kwargs.get('data', {})
            result = kwargs.get('result')
            for record in result:
                if 'name' in record:
                    obj_id = f"{record['name']} ({record['id']})"
                    id_type = "namn och databas-id"
                else:
                    obj_id = f"{record['id']}"
                    id_type = "databas-id"
                # Translate to human readable
                record_hr = self._af_audit_log_human_readable_vals(record, model=model)
                # Remove extra fields from log record
                for field in data.get('extra_fields', []):
                    record_hr.pop(field)
                log.append({
                    'obj_type': f"{model._description} ({model._name})",
                    'obj_id': obj_id,
                    'id_type': id_type,
                    'values': record_hr,
                })
        elif operation == 'UPDATE':
            # ids: record ids
            # values: write values
            # data: read from before update (_af_audit_log_pre_method)
            # result: write result (useless?)
            values = kwargs.get('values', {})
            data = kwargs.get('data')
            if data is None:
                # before generation failed
                data = {
                    'values': {},
                    'extra_fields': [],
                }
            for vals_pre in data.get('values'):
                if 'name' in values:
                    obj_id = f"{values['name']} ({vals_pre['id']})"
                    id_type = "namn och databas-id"
                elif 'name' in vals_pre:
                    obj_id = f"{vals_pre['name']} ({vals_pre['id']})"
                    id_type = "namn och databas-id"
                else:
                    obj_id = f"{vals_pre['id']}"
                    id_type = "databas-id"
                vals_hr = self._af_audit_log_human_readable_vals(values)
                vals_pre = self._af_audit_log_human_readable_vals(vals_pre)
                for key, val in vals_hr.items():
                    vals_hr[key] = (
                        vals_hr[key][0],
                        f"{vals_pre.get(key, (None, '*SAKNAS*'))[1]} => {vals_hr[key][1]}")
                log.append({
                    'obj_type': f"{model._description} ({model._name})",
                    'obj_id': obj_id,
                    'id_type': id_type,
                    'values': vals_hr,
                })
        elif operation == 'SEARCH':
            # result: search_read result
            # search_terms: search domain
            # data: read from before update (_af_audit_log_pre_method)
            # TODO: Its currently not possible to recognise 0 hits
            #       searches. Try to determine from domain if this is a
            #       jobseeker search.
            search_terms = kwargs.get('search_terms')
            result = kwargs.get('result')

            search_logs = OrderedDict()
            search_terms_hr = self._af_audit_log_domain2search_terms(search_terms)

            data = kwargs.get('data', {})
            search_log = None
            for record in result:
                if not search_log:
                    if 'name' in record:
                        obj_id = f"{record['name']} ({record['id']})"
                        id_type = "namn och databas-id"
                    else:
                        obj_id = f"{record['id']}"
                        id_type = "databas-id"
                    search_log = {
                        'obj_type': f"{model._description} ({model._name})",
                        'obj_id': obj_id,
                        'id_type': id_type,
                        'values': {
                            '#hits': 1,
                            'search_terms': search_terms_hr,
                        },
                    }
                else:
                    search_log['values']['#hits'] += 1
            log.append(search_log)
        elif operation == 'DELETE':
            # ids: record ids
            # values: read from before unlink (_af_audit_log_pre_method)
            setup = self._af_audit_log_get_setup()
            values = kwargs.get('values', {})
            for record in values:
                if 'name' in record:
                    obj_id = f"{record['name']} ({record['id']})"
                    id_type = "namn och databas-id"
                else:
                    obj_id = f"{record['id']}"
                    id_type = "databas-id"
                log.append({
                    'obj_type': f"{model._description} ({model._name})",
                    'obj_id': obj_id,
                    'id_type': id_type,
                })
        return log
