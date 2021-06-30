#  Copyright (c) 2021 Arbetsförmedlingen.

import json

from odoo import http, _
from odoo.http import request
from odoo.addons.web.controllers.main import DataSet as DataSetOrigin
from odoo.models import Model
from odoo.exceptions import UserError
from odoo.addons.web.controllers.main import CSVExport as CSVExportOrigin,\
    ExcelExport as ExcelExportOrigin, serialize_exception
import operator

import logging
_logger = logging.getLogger(__name__)


class AfLogMixin(object):
    """ Mixin for audit logged controllers.
    """

    def _get_audit_user(self) -> Model:
        """Return the actual user that logged in. Will return original
        user if currently logged in as Odoo Bot."""
        user = request.env.user
        if request.session.get('login') and request.session['login'] != user.login:
            # User is OdooBot. Find original user from session.
            user = user.search([('login', '=', request.session['login'])])
            user = user or request.env.user
        return user.sudo()

    def _is_af_audit_log_model(self, model: Model) -> bool:
        """ Check if the model has audit logging.
        """
        if hasattr(model, '_af_audit_log'):
            return model._af_audit_log
        return False

    def _af_log_pre_method_call(self, model: str, method: str, args: list,
                                kwargs: dict) -> tuple:
        """ Run before a method call.
        :returns: (the user object, the model object, whether this is an
                  audit model, pre-method data, pre-method data for
                  admin logging)
        """
        user = model_obj = audit = before = admin_before = None
        try:
            user = self._get_audit_user()
            model_obj = request.env[model].sudo()
            audit = self._is_af_audit_log_model(model_obj)
            before = admin_before = None
            if audit:
                before = model_obj._af_audit_log_pre_method(
                    user, method, args, kwargs)
            if user.has_group('base.group_system'):
                admin_before = user._af_audit_log_pre_admin_action(model_obj, method, args, kwargs)

        except:
            _logger.exception("AUDIT LOG FAILURE! Failed to generate data for audit log.")
        return user, model_obj, audit, before, admin_before

    def _af_log_post_method_call(self, user: Model, model_obj: Model, audit: bool,
                                 method: str, args: list, kwargs: dict, before,
                                 admin_before, res, error: Exception):
        if audit:
            try:
                model_obj._af_audit_log_post_method(
                    user, method, args, kwargs,
                    res, before, error)
            except:
                _logger.exception(
                    f"AUDIT LOG FAILURE! Failed to generate audit log. model: {model_obj._name},"
                    f" method: {method}")
        # Audit log admin actions
        if user.has_group('base.group_system'):
            try:
                user._af_audit_log_post_admin_action(
                    model_obj, method, args, kwargs, res, admin_before, error)
            except:
                _logger.exception(
                    f"AUDIT LOG FAILURE! Failed to generate admin audit log. model: {model_obj._name},"
                    f" method: {method}")
        if audit:
            try:
                model_obj._af_audit_log_cleanup(
                    user, method, args, kwargs,
                    res, before)
            except:
                _logger.exception(
                    f"AUDIT LOG FAILURE! Failed to clean up after admin log. model: {model_obj._name},"
                    f" method: {method}")


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
        res = error = None
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


class CSVExport(CSVExportOrigin, AfLogMixin):

    @http.route('/web/export/csv', type='http', auth="user")
    @serialize_exception
    def index(self, data, token):
        params = json.loads(data)
        model, fields, ids, domain, import_compat = \
            operator.itemgetter('model', 'fields', 'ids', 'domain', 'import_compat')(params)
        fields = [f['name'] for f in fields]
        try:
            if not ids:
                ids = [r['id'] for r in request.env[model].search_read(
                    domain, ['id'], offset=0, limit=False, order=False)]
        except:
            # Super should throw the same error. Handle it there.
            pass

        args = [ids, fields]
        kwargs = {}
        user, model_obj, audit, before, admin_before = self._af_log_pre_method_call(
            model, 'read', args, kwargs)
        res = error = None
        read_data = None
        try:
            # TODO: Remove this read. Move this functionality to
            #  the method base (in the super call).
            read_data = model_obj.search_read([('id', 'in', ids)], fields)
            res = super(CSVExport, self).index(data, token)
        except Exception as e:
            error = e
        self._af_log_post_method_call(user, model_obj, audit, 'read', args,
                                      kwargs, before, admin_before,
                                      read_data, error)
        if error:
            raise error from None
        return res


class ExcelExport(ExcelExportOrigin, AfLogMixin):

    @http.route('/web/export/xls', type='http', auth="user")
    @serialize_exception
    def index(self, data, token):
        params = json.loads(data)
        model, fields, ids, domain, import_compat = \
            operator.itemgetter('model', 'fields', 'ids', 'domain', 'import_compat')(params)
        fields = [f['name'] for f in fields]
        try:
            if not ids:
                ids = [r['id'] for r in request.env[model].search_read(
                    domain, ['id'], offset=0, limit=False, order=False)]
        except:
            # Super should throw the same error. Handle it there.
            pass

        args = [ids, fields]
        kwargs = {}
        user, model_obj, audit, before, admin_before = self._af_log_pre_method_call(
            model, 'read', args, kwargs)
        res = error = None
        read_data = None
        try:
            # TODO: Remove this read. Move this functionality to
            #  the method base (in the super call).
            read_data = model_obj.search_read([('id', 'in', ids)], fields)
            res = super(ExcelExport, self).index(data, token)
        except Exception as e:
            error = e
        self._af_log_post_method_call(user, model_obj, audit, 'read', args,
                                      kwargs, before, admin_before,
                                      read_data, error)
        if error:
            raise error from None
        return res
