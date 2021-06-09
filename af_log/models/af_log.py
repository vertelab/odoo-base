#  Copyright (c) 2021 Arbetsförmedlingen.

from odoo import fields, models, api
from odoo.exceptions import AccessError
from copy import deepcopy
from .tools import _get_request_object, recursive_default, recursive_update
from collections import OrderedDict
import logging

_logger = logging.getLogger(__name__)

TECH2HR = {}

AUDIT_LOG_SETUP = {}


class AFLogAudit(models.AbstractModel):
    _name = 'af.log.audit'
    _description = 'Arbetsförmedlingen Audit Log'
    _af_audit_log = True

    @api.model
    def _af_audit_log_setup(self):
        """ Define the audit log setup for this model. Several
        different object types can be defined. Needs to be
        overwritten in implementing models.
        :return: {
            'audit_types': {
                'TECHNICAL_OBJECT_NAME': {
                    'type': 'HR object type',
                    'id_type': 'HR id type',
                    'id': 'FIELD_NAME',  # field name (str) or function (NOT IMPLEMENTED) to generate id
                    'required_fields': ['field_1', 'field_2', ...], # Fields required to identify this object type
                    'filter': lambda model, values: values['is_jobseeker'],  # Filter function to identify object type
                    'priority': 1, # Lower number has higher priority
                }
            }
        }
        """
        return {}

    @api.model
    def _af_audit_log_get_setup(self):
        """ Fetch the audit log setup for this model. Will cache the
        result. Do not override.
        """
        if self._name not in AUDIT_LOG_SETUP:
            setup = self._af_audit_log_setup()
            # Aggregate required_fields from all audit types
            setup['required_fields'] = []
            for k, v in setup['audit_types'].items():
                for field in v['required_fields'] + \
                             [v['id']] if isinstance(v['id'], str) else []:
                    if field not in setup['required_fields']:
                        setup['required_fields'].append(field)
            # Reorder audit_types by priority
            setup['audit_types'] = OrderedDict(sorted(
                setup['audit_types'].items(),
                key=lambda x: x[1].get('priority', 100)))
            AUDIT_LOG_SETUP.setdefault(self._name, setup)
        return AUDIT_LOG_SETUP.get(self._name)

    @api.model
    def _af_audit_log_field_data(self, model_name, f, v):
        model = self.env[model_name]
        field = model._fields.get(f)
        if not field:
            _logger.warning(f"TECH2HR: No field named {f} in {model_name}")
            return
        field_data = {
            'model': model_name,
            'label': field._description_string(self.env),
        }

    @api.model
    def _af_audit_log_human_readable_vals(self, values, write=False):
        """ Translate technical values to human readable format.
            :param values: The values to translate.
            :param write: True if values is write/create values.
        """
        # TODO: Implement the translation. How hard could it be?
        # TODO: The syntax differs between read and write/create values.
        #  Need more hr conversion methods...
        # Cache in TECH2HR. Keep it thread safe!
        # setdefault should be useful.
        result = {}
        for k, v in values.items():
            # field_name: (HR field name, HR value)
            result[k] = (k, v)
        return result
        # label = self._fields['registered_through']._description_string(self.env)
        # self._fields['country_id'].convert_to_display_name(self.env.ref('base.se'), self)
        for f, v in values.items():
            field_data = TECH2HR.get(f'{self._name},{f}')
            if not field_data:
                field = self._fields.get(f)
                if not field:
                    _logger.warning(f"TECH2HR: No field named {f} in {self._name}")
        return values

    @api.model
    def _af_audit_log_domain2search_terms(self, domain):
        # TODO: Implement domain translation to human readable format.
        # Cache in TECH2HR. Keep it thread safe!
        # setdefault should be useful.
        return str(domain)

    @api.model
    def _af_audit_log_get_id(self, audit_data, values):
        """ Return the object id for an audit log record.
        :param audit_data: The setup data for this audit type.
        :param values: Record values for the logged object.
        :returns: A string with the object id."""
        id_mehod = audit_data.get('id')
        if isinstance(id_mehod, str):
            return values.get(id_mehod)
        elif callable(id_mehod):
            return id_mehod(self.env, values)
        raise Warning(f"Something went wrong when evaluating id in audit logging. Setup: {audit_data}")

    @api.model
    def _af_audit_log_cruds(self, user, operation, **kwargs):
        """ Generate a CRUDS audit log. Implement audit logging of
        model specific methods here.
        :arg user: The logged in user.
        :arg operation: The operation. One of CREATE, READ, UPDATE,
        DELETE or SEARCH.
        :arg ids: The ids of the records affected by the operation.
        :arg data: Data from a read/search operation. Original data when
        writing. Use this instead of browse if possible.
        :arg search_terms: The search domain.
        :arg result: The result of a function call.
        :arg error: Error during execution.
        """
        log_objs = self._af_audit_log_details(operation, **kwargs)
        if not log_objs:
            # Nothing to log
            return
        request = _get_request_object()
        audit_log = {
            'user': user._af_log_record(),
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
                info = [f'{v[0]}={v[1]}' for v in obj['values'].values()]
                log_record['audit']['objectinfo'] = info
            elif operation == 'UPDATE':
                info = [f'{v[0]}={v[1]}' for v in obj['values'].values()]
                log_record['audit']['objectinfo'] = info
            elif operation == 'DELETE':
                pass
            elif operation == 'SEARCH':
                # audit.searchstring: What the user entered.
                # audit.searchparams: Extra search parameters.
                # We can't really separate what the user entered from
                # what was automagically added by the frontend.
                log_record['audit']['searchstring'] = obj['values']['search_terms']
                log_record['audit']['objectinfo'] = obj['values']['#hits']
            recursive_default(log_record, obj.get('defaults', {}))
            recursive_update(log_record, obj.get('update', {}))
            _logger.warning('Audit log monkeypatch not installed.', extra={'json_log_data': log_record})

    @api.model
    def _af_audit_log_details(self, operation, **kwargs):
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
            # values: create vals
            # result: create result ( so... recordset or id?)
            setup = self._af_audit_log_get_setup()
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
                for audit_type, audit_data in setup['audit_types'].items():
                    if audit_data['filter'](self.env, record or value):
                        obj_id = self._af_audit_log_get_id(audit_data, record) or \
                                 self._af_audit_log_get_id(audit_data, value) or 'OKÄND'
                        log.append({
                            'obj_type': audit_data['type'],
                            'obj_id': obj_id,
                            'id_type': audit_data['id_type'],
                            'values': self._af_audit_log_human_readable_vals(values),
                        })
        elif operation == 'READ':
            # ids: record ids
            # data: read from before update (_af_audit_log_pre_method)
            # result: read values
            setup = self._af_audit_log_get_setup()
            data = kwargs.get('data', {})
            result = kwargs.get('result')
            for record in result:
                # Check all audit types for this model
                for audit_type, audit_data in setup['audit_types'].items():
                    if audit_data['filter'](self.env, record):
                        # We found our matching type
                        audit_id = self._af_audit_log_get_id(audit_data, record) or 'OKÄND'
                        # Translate to human readable
                        record_hr = self._af_audit_log_human_readable_vals(record)
                        # Remove extra fields from log record
                        for field in data.get('extra_fields', []):
                            record_hr.pop(field)
                        log.append({
                            'obj_type': audit_data['type'],
                            'obj_id': audit_id,
                            'id_type': audit_data['id_type'],
                            'values': record_hr,
                        })
                        # Only create one log entry per record
                        break
        elif operation == 'UPDATE':
            # ids: record ids
            # values: write values
            # data: read from before update (_af_audit_log_pre_method)
            # result: write result (useless?)
            setup = self._af_audit_log_get_setup()
            values = kwargs.get('values', {})
            data = kwargs.get('data')
            if data is None:
                # before generation failed
                data = {
                    'values': {},
                    'extra_fields': [],
                }
            for vals_pre in data.get('values'):
                # Check all audit types for this model
                for audit_type, audit_data in setup['audit_types'].items():
                    if audit_data['filter'](self.env, vals_pre):
                        # We found our type
                        vals_hr = self._af_audit_log_human_readable_vals(values)
                        vals_pre = self._af_audit_log_human_readable_vals(vals_pre)
                        for key, val in vals_hr.items():
                            vals_hr[key] = (
                                vals_hr[key][0],
                                f"{vals_pre.get(key, (None, '*SAKNAS*'))[1]} => {vals_hr[key][1]}")
                        log.append({
                            'obj_type': audit_data['type'],
                            'obj_id': self._af_audit_log_get_id(audit_data, values)
                                      or 'OKÄND',
                            'id_type': audit_data['id_type'],
                            'values': vals_hr,
                        })
                        # Only create one log entry per record
                        break
        elif operation == 'SEARCH':
            # result: search_read result
            # search_terms: search domain
            # data: read from before update (_af_audit_log_pre_method)
            # TODO: Its currently not possible to recognise 0 hits
            #       searches. Try to determine from domain if this is a
            #       jobseeker search.
            # TODO: Implement support for the search method.
            search_terms = kwargs.get('search_terms')
            result = kwargs.get('result')

            search_logs = OrderedDict()
            search_terms_hr = None

            setup = self._af_audit_log_get_setup()
            data = kwargs.get('data', {})
            for record in result:
                # Check all audit types for this model
                for audit_type, audit_data in setup['audit_types'].items():
                    if audit_data['filter'](self.env, record):
                        # We found our matching type
                        if audit_type not in search_logs:
                            if not search_terms_hr:
                                search_terms_hr = self._af_audit_log_domain2search_terms(search_terms)
                            search_logs[audit_type] = {
                                'obj_type': audit_data['type'],
                                'obj_id': self._af_audit_log_get_id(audit_data, record)
                                          or 'OKÄND',
                                'id_type': audit_data['id_type'],
                                'values': {
                                    '#hits': 1,
                                    'search_terms': search_terms_hr,
                                },
                            }
                        else:
                            search_logs[audit_type]['values']['#hits'] += 1
                        # Only create one log entry per record
                        break
            log += search_logs.values()
        elif operation == 'DELETE':
            # ids: record ids
            # values: read from before unlink (_af_audit_log_pre_method)
            setup = self._af_audit_log_get_setup()
            values = kwargs.get('values', {})
            for record in values:
                for audit_type, audit_data in setup['audit_types'].items():
                    if audit_data['filter'](self.env, record):
                        log.append({
                            'obj_type': audit_data['type'],
                            'obj_id': self._af_audit_log_get_id(audit_data, record)
                                      or 'OKÄND',
                            'id_type': audit_data['id_type'],
                        })
                        # Only create one log entry per record
                        break
        return log

    @api.model
    def _af_audit_log_pre_method(self, user, method, args, kwargs):
        """ Run before a method call.
        :arg method: The method being called.
        :arg args: The arguments to the method.
        :arg kwargs: The keyword arguments to the method.
        :returns: Some data needed for audit log generation in
        _af_audit_log_post_method."""
        if method in ('read', 'search_read'):
            fields = (len(args) > 1 and args[1]) or kwargs.get('fields')
            if not fields:
                # Every field will be read. Nothing to do here.
                return {}
            setup = self._af_audit_log_get_setup()
            # Add fields needed for object type filtering
            extra_fields = []
            for field in setup['required_fields']:
                if field not in fields and field not in extra_fields:
                    fields.append(field)
                    extra_fields.append(field)
            return {'extra_fields': extra_fields}
        elif method == 'write':
            # Save values before write
            ids = args[0]
            values = args[1]
            fields = [key for key in values]
            setup = self._af_audit_log_get_setup()
            # Add fields needed for object type filtering
            extra_fields = []
            for field in setup['required_fields']:
                if field not in fields and field not in extra_fields:
                    extra_fields.append(field)
            return {
                'values': self.sudo().search_read([('id', 'in', ids)], fields + extra_fields),
                'extra_fields': extra_fields
            }
        elif method == 'unlink':
            # Save values before unlink
            ids = args[0]
            return self.sudo().search_read([('id', 'in', ids)])

    @api.model
    def _af_audit_log_post_method(self, user, method, args, kwargs, res, before=None, error=None):
        """ Generate an audit log from a function call.
        :arg user: The user executing this method.
        :arg method: The method being called.
        :arg args: The arguments to the method.
        :arg kwargs: The keyword arguments to the method.
        :arg before: Data from _af_audit_log_pre_method, generated
                     before the method call.
        :arg res: The result of the method call.
        """
        if method == 'create':
            self._af_audit_log_cruds(user, 'CREATE', values=args[0], result=res)
        elif method == 'read':
            self._af_audit_log_cruds(user, 'READ', ids=args[0], result=res)
        elif method == 'write':
            self._af_audit_log_cruds(user, 'UPDATE', ids=args[0], values=args[1], data=before, result=res)
        elif method == 'unlink':
            self._af_audit_log_cruds(user, "DELETE", ids=args[0], values=before)
        elif method == 'search_read':
            if len(args) > 0:
                domain = args[0]
            else:
                domain = kwargs.get('domain')
            if len(res) == 1:
                # Endast ett sökresultat ska tolkas som en READ
                self._af_audit_log_cruds(user, "READ", ids=[r['id'] for r in res], result=res)
            else:
                # Flera/inget sökresultat ska tolkas som en SEARCH
                self._af_audit_log_cruds(user, "SEARCH", result=res, search_terms=domain)

    @api.model
    def _af_audit_log_cleanup(self, user, method, args, kwargs, res, before):
        """ Perform cleanup before returning results."""
        if method in ('read', 'search_read'):
            before = before or {}
            # Remove extra fields from result before returning
            for record in res:
                for field in before.get('extra_fields', {}):
                    if field in record:
                        del record[field]
