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


class AfLogMixin(object):
    """ Mixin for audit logged controllers.
    """

    def _get_audit_user(self):
        """Return the actual user that logged in. Will return original
        user if currently logged in as Odoo Bot."""
        user = request.env.user
        if request.session.get('login') and request.session['login'] != user.login:
            # User is OdooBot. Find original user from session.
            user = user.search([('login', '=', request.session['login'])])
            user = user or request.env.user
        return user.sudo()

    def _is_af_audit_log_model(self, model):
        """ Check if the model has audit logging.
        """
        if hasattr(model, '_af_audit_log'):
            return model._af_audit_log
        return False

    def _af_log_pre_method_call(self, model, method, args, kwargs):
        user = self._get_audit_user()
        model_obj = request.env[model].sudo()
        audit = self._is_af_audit_log_model(model_obj)
        before = admin_before = None
        if audit:
            before = model_obj._af_audit_log_pre_method(
                user, method, args, kwargs)
        if user.has_group('base.group_system'):
            admin_before = user._af_audit_log_pre_admin_action(model_obj, method, args, kwargs)
        return user, model_obj, audit, before, admin_before

    def _af_log_post_method_call(self, user, model_obj, audit, method, args, kwargs,
                                 before, admin_before, res, error):
        if audit:
            try:
                model_obj._af_audit_log_post_method(
                    user, method, args, kwargs,
                    res, before, error)
            except:
                _logger.exception(
                    f"Failed to generate audit log! model: {model_obj._name},"
                    f"method: {method}")
        # Audit log admin actions
        if user.has_group('base.group_system'):
            try:
                user._af_audit_log_post_admin_action(
                    model_obj, method, args, kwargs, res, admin_before, error)
            except:
                _logger.exception(
                    f"Failed to generate admin audit log! model: {model_obj._name},"
                    f"method: {method}")
        if audit:
            model_obj._af_audit_log_cleanup(
                user, method, args, kwargs,
                res, before)


class DataSet(DataSetOrigin, AfLogMixin):

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
        args = [domain, fields]
        kwargs = {'limit': limit, 'domain': domain, 'sort': sort}
        user, model_obj, audit, before, admin_before = self._af_log_pre_method_call(
            model, 'search_read', args, kwargs)
        error = None
        try:
            res = super(DataSet, self).do_search_read(
                model, fields=fields, offset=offset, limit=limit,
                domain=domain, sort=sort)
        except Exception as e:
            error = e
        self._af_log_post_method_call(user, model_obj, audit, 'search_read', args,
                                      kwargs, before, admin_before,
                                      res.get('records', {}), error)
        if error:
            raise error from None
        return res

    def _call_kw(self, model, method, args, kwargs):
        # Called by
        # call_common
        # call          /web/dataset/call
        # call_kw       /web/dataset/call_kw
        # call_button   /web/dataset/call_button
        user, model_obj, audit, before, admin_before = self._af_log_pre_method_call(
            model, method, args, kwargs)
        # Run the called method
        res = error = None
        try:
            res = super(DataSet, self)._call_kw(model, method, args, kwargs)
        except Exception as e:
            # Save error for re-raise
            error = e
        self._af_log_post_method_call(user, model_obj, audit, method, args,
                                      kwargs, before, admin_before, res, error)
        # Re-raise caught error
        if error:
            raise error from None
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
        # This is an UPDATE. It is limited to integer fields.
        res = super(DataSet, self).resequence(model, ids, field, offset=offset)
        return res


    @http.route('/web/dataset/load', type='json', auth="user")
    def load(self, model, id, fields):
        user = self._get_audit_user()
        model_obj = request.env[model].sudo()
        audit = self._is_af_audit_log_model(model_obj)
        if audit:
            # fields is never used, so no need to pass it on here.
            args = [[id]]
            kwargs = {}
            try:
                before = model_obj._af_audit_log_pre_method(
                    user, 'read', args, kwargs)
            except:
                before = None
                _logger.exception(
                    "Failed to generate before data for audit log! "
                    f"model: {model_obj._name} method: search_read")
        error = None
        try:
            res = super(DataSet, self).load(model, id, fields)
        except Exception as e:
            error = e
        if audit:
            try:
                model_obj._af_audit_log_post_method(
                    user, 'read', args, kwargs,
                    [res.get('value', {})], before, error)
            except:
                _logger.exception(
                    f"Failed to generate audit log! model: {model_obj._name},"
                    f"method: search_read")
        if error:
            raise error from None
        elif audit:
            model_obj._af_audit_log_cleanup(
                user, 'read', args, kwargs,
                [res.get('value', {})], before)
        return res
