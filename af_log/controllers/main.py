#  Copyright (c) 2021 Arbetsförmedlingen.

import json

from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import DataSet as DataSetOrigin

# TODO: What to do about these controllers?
#       I feel like they should be disabled altogether.
# from odoo.addons.web.controllers.main import Export, CSVExport, ExcelExport

import logging
_logger = logging.getLogger(__name__)


class DataSet(DataSetOrigin):

    def _is_af_audit_log_model(self, model):
        """ Check if the model has audit logging.
        """
        if hasattr(model, '_af_audit_log'):
            return model._af_audit_log
        return False

    def do_search_read(self, model, fields=False, offset=0, limit=False, domain=None
                       , sort=None):
        """ Performs a search() followed by a read() (if needed) using the
        provided search criteria

        :param str model: the name of the model to search on
        :param fields: a list of the fields to return in the result records
        :type fields: [str]
        :param int offset: from which index should the results start being returned
        :param int limit: the maximum number of records to return
        :param list domain: the search domain for the query
        :param list sort: sorting directives
        :returns: A structure (dict) with two keys: ids (all the ids matching
                  the (domain, context) pair) and records (paginated records
                  matching fields selection set)
        :rtype: list
        """
        # Called by
        # search_read   /web/dataset/search_read
        def audit_log(model, res, domain, error=None):
            try:
                model_obj = request.env[model]
                if self._is_af_audit_log_model(model_obj):
                    if len(res) == 1:
                        # Endast ett sökresultat ska tolkas som en READ
                        model_obj._af_cruds_audit_log("READ", ids=[r['id'] for r in res], result=res, error=error)
                    else:
                        # Flera/inget sökresultat ska tolkas som en SEARCH
                        model_obj._af_cruds_audit_log("SEARCH", result=res,
                                                      search_terms=domain,
                                                      error=error)
            except:
                _logger.exception(f"""Failed to generate audit log! model: {model}, method: do_search_read""")
        try:
            res = super(DataSet, self).do_search_read(model, fields=fields,
                                                  offset=offset, limit=limit,
                                                  domain=domain, sort=sort)
        except Exception as e:
            audit_log(model, res, domain, e)
            raise
        audit_log(model, res, domain)
        return res

    def _call_kw(self, model, method, args, kwargs):
        # Called by
        # call_common
        # call          /web/dataset/call
        # call_kw       /web/dataset/call_kw
        # call_button   /web/dataset/call_button
        def audit_log(model_obj, method, args, kwargs, res, before, error=None):
            try:
                model_obj._af_post_func_audit_log(method, args, kwargs, res, before)
            except:
                _logger.exception(
                    f"Failed to generate audit log! model: {model_obj._name},"
                    f"method: {method}")
        model_obj = request.env[model]
        audit = self._is_af_audit_log_model(model_obj)
        if audit:
            try:
                before = model_obj._af_pre_func_audit_log(method, args, kwargs)
            except:
                # Stop further audit execution
                audit = False
                _logger.exception(
                    "Failed to generate before data for audit log! "
                    f"model: {model_obj._name} method: {method}")
        res = None
        try:
            res = super(DataSet, self)._call_kw(model, method, args, kwargs)
        except Exception as e:
            if audit:
                audit_log(model_obj, method, args, kwargs, res, before, e)
            raise
        if audit:
            audit_log(model_obj, method, args, kwargs, res, before)
        return res

    # TODO: Behöver vi övervaka denna? Det är en UPDATE, men väldigt
    #       begränsat vad som kan skrivas.
    @http.route('/web/dataset/resequence', type='json', auth="user")
    def resequence(self, model, ids, field='sequence', offset=0):
        """ Re-sequences a number of records in the model, by their ids

        The re-sequencing starts at the first model of ``ids``, the sequence
        number is incremented by one after each record and starts at ``offset``

        :param ids: identifiers of the records to resequence, in the new sequence order
        :type ids: list(id)
        :param str field: field used for sequence specification, defaults to
                          "sequence"
        :param int offset: sequence number for first record in ``ids``, allows
                           starting the resequencing from an arbitrary number,
                           defaults to ``0``
        """
        # This is an UPDATE. Can it be run wth any field as input? What
        # would it do for a char or many2many?
        res = super(DataSet, self).resequence(model, ids, field, offset=offset)
        return res

    # TODO: När används denna? Hittar inget i koden. Kan vi stänga av den?
    # fields används inte. Det ser trasigt ut.
    # @http.route('/web/dataset/load', type='json', auth="user")
    # def load(self, model, id, fields):
    #     _logger.warn(f"load model: {model} fields: {fields} id: {id}")
    #     res = super(DataSet, self).load(model, id, fields)
    #     _logger.warn(f"load res: {res}")
    #     return res
