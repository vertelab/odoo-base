odoo.define('web_extra_options.basic_fields', function (require) {
"use strict";

let Domain = require('web.Domain');
let BasicModel = require('web.BasicModel');

/**
 * The "Domain" field allows the user to construct a technical-prefix domain
 * thanks to a tree-like interface and see the selected records in real time.
 * In debug mode, an input is also there to be able to enter the prefix char
 * domain directly (or to build advanced domains the tree-like interface does
 * not allow to).
 */
BasicModel.include({
    /**
     * Fetches the number of records associated to the domain the value of the
     * given field represents.
     *
     * @param {Object} record - an element from the localData
     * @param {Object} fieldName - the name of the field
     * @param {Object} fieldInfo
     * @returns {Deferred<any>}
     *          The deferred is resolved with the fetched special data. If this
     *          data is the same as the previously fetched one (for the given
     *          parameters), no RPC is done and the deferred is resolved with
     *          the undefined value.
     */
    _fetchSpecialDomain: function (record, fieldName, fieldInfo) {
        var context = record.getContext({fieldName: fieldName});

        var domainModel = fieldInfo.options.model;
        if (record.data.hasOwnProperty(domainModel)) {
            domainModel = record._changes && record._changes[domainModel] || record.data[domainModel];
        }
        var domainValue = record._changes && record._changes[fieldName] || record.data[fieldName] || [];

        // avoid rpc if not necessary
        var hasChanged = this._saveSpecialDataCache(record, fieldName, {
            context: context,
            domainModel: domainModel,
            domainValue: domainValue,
        });
        if (!hasChanged) {
            return $.when();
        } else if (!domainModel) {
            return $.when({
                model: domainModel,
                nbRecords: 0,
            });
        }

        var def = $.Deferred();
        var evalContext = this._getEvalContext(record);
        let args = [Domain.prototype.stringToArray(domainValue, evalContext)];
        // Check for custom search_count method.
        let method = fieldInfo.options.method || "search_count";
        let model = domainModel;
        if (method !== "search_count"){
             model = record.model;
             args.push(domainModel)
        }
        let promise = this._rpc({
            model: model,
            method: method,
            args: args,
            context: context
        });
        if (method == "search_count"){
            promise.then(_.identity, function (error, e) {
                e.preventDefault(); // prevent traceback (the search_count might be intended to break)
                return false;
            })}
        promise.always(function (nbRecords) {
            def.resolve({
                model: domainModel,
                nbRecords: nbRecords,
            });
        });

        return def;
    }
});
});
