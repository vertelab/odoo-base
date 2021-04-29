#  Copyright (c) 2021 Arbetsförmedlingen.

from odoo import fields, models, api
from odoo.exceptions import AccessError
from copy import deepcopy

import logging
_logger = logging.getLogger(__name__)

TECH2HR = {}

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

class AFLogAudit(models.AbstractModel):
    _name = 'af.log.audit'
    _description = 'Arbetsförmedlingen Audit Log'
    _af_audit_log = True

    @api.model
    def _af_log_human_readable_vals(self, values):
        # TODO: Implement the translation. How hard could it be?
        # Cache in TECH2HR. Keep it thread safe!
        # setdefault should be useful.
        return values

    @api.model
    def _af_log_domain2search_terms(self, domain):
        # TODO: Implement domain translation to human readable format.
        # Cache in TECH2HR. Keep it thread safe!
        # setdefault should be useful.
        return str(domain)

    @api.model
    def _af_cruds_audit_log(self, operation, **kwargs):
        """ Generate a CRUDS audit log. Needs to be implemented by all inheriting
        models.
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
        audit_log = {
            'user': self.env.user._af_log_record(),
            'event': {'action': operation},
            'source': {'ip': '1.2.3.4'},  # TODO: Fix IP both here and in apache httpd
            'audit': {
                'executioninfo': 1,
            }
        }
        if kwargs.get('error'):
            if type(kwargs.get('error')) == AccessError:
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
                info = [f'{k}={v}' for k, v in obj['values'].items()]
                log_record['audit']['objectinfo'] = info
            elif operation == 'UPDATE':
                info = [f'{k}={v}' for k, v in obj['values'].items()]
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
            _logger.warning('Audit log monkeypatch not installed.', extra={'audit_log': log_record})

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
        # elif operation == 'READ':
        #     # ids: record ids
        #     # result: read values
        #     pass
        # elif operation == 'UPDATE':
        #     # ids: record ids
        #     # values: write values
        #     # data: read from before update (_af_pre_func_audit_log)
        #     # result: write result (useless?)
        #     pass
        # elif operation == 'DELETE':
        #     # ids: record ids
        #     # values: read from before unlink (_af_pre_func_audit_log)
        #     pass
        # elif operation == 'SEARCH':
        #     # result: search_read result
        #     # search_terms: search domain
        #     pass
        return log

    @api.model
    def _af_pre_func_audit_log(self, method, args, kwargs):
        """ Run before a function call.
        :arg method: The method being called.
        :arg args: The arguments to the method.
        :arg kwargs: The keyword arguments to the method.
        :returns: Some data needed for audit log generation in
        _af_post_func_audit_log."""
        if method == 'write':
            # Save values before write
            ids = args[0]
            values = args[1]
            fields = [key for key in values]
            return self.sudo().search_read([('id', 'in', ids)], fields)
        elif method == 'unlink':
            # Save values before unlink
            ids = args[0]
            return self.sudo().search_read([('id', 'in', ids)])

    @api.model
    def _af_post_func_audit_log(self, method, args, kwargs, res, before=None):
        """ Generate an audit log from a function call.
        :arg method: The method being called.
        :arg args: The arguments to the method.
        :arg kwargs: The keyword arguments to the method.
        :arg before: Data from _af_pre_func_audit_log, generated before
        the method call.
        :arg res: The result of the method call.
        """
        if method == 'create':
            self._af_cruds_audit_log('CREATE', values=args[0], result=res)
        elif method == 'read':
            self._af_cruds_audit_log('READ', ids=args[0], result=res)
        elif method == 'write':
            self._af_cruds_audit_log('UPDATE', ids=args[0], values=args[1], data=before, result=res)
        elif method == 'unlink':
            self._af_cruds_audit_log("DELETE", ids=args[0], values=before)
        elif method == 'search_read':
            if len(args) > 0:
                domain = args[0]
            else:
                domain = kwargs.get('domain')
            if len(res) == 1:
                # Endast ett sökresultat ska tolkas som en READ
                self._af_cruds_audit_log("READ", ids=[r['id'] for r in res], result=res)
            else:
                # Flera/inget sökresultat ska tolkas som en SEARCH
                self._af_cruds_audit_log("SEARCH", result=res, search_terms=domain)



