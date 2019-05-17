odoo.define('web.ListViewDecorations', function (require) {
"use strict";

var data_manager = require('web.data_manager');
var session = require('web.session');
var ListView = require('web.ListView');


function compute_custom_decorations(view) {
    var self = view;
    // Retrieve the decoration defined on the model's list view
    view.custom_decorations = _.pick(view.fields_view.arch.attrs, function(value, key) {
        return key.startsWith('custom-decoration-');
    });
    view.custom_decorations = _.mapObject(view.custom_decorations, function(value) {
        return py.parse(py.tokenize(value));
    });
    var fields_def = data_manager.load_fields(view.dataset).then(function(fields_get) {
        self.fields_get = fields_get;
    });
    return $.when(view, fields_def);
}
    
ListView.include({
    compute_decoration_classnames: function (record) {
        // FFS! How is it that javascript STILL can't fucking handle some simple motherfucking inheritance?
        // Anything I try to add to ListView gets lost as soon as super is called.
        // It really seems to be impossible to override stuff.
        if (this.custom_decorations === undefined) {
            compute_custom_decorations(this);
        }
        var classnames= '';
        var context = _.extend({}, record.attributes, {
            uid: session.uid,
            current_date: moment().format('YYYY-MM-DD')
            // TODO: time, datetime, relativedelta
        });
        _.each(this.decoration, function(expr, decoration) {
            if (py.PY_isTrue(py.evaluate(expr, context))) {
                classnames += ' ' + decoration.replace('decoration', 'text');
            }
        });
        _.each(this.custom_decorations, function(expr, decoration) {
            if (py.PY_isTrue(py.evaluate(expr, context))) {
                classnames += ' ' + decoration.replace('custom-decoration-', '');
            }
        });
        return classnames;
    },
});


})
