odoo.define('adjust_errormsg_time.AttachDocument', function (require) {
    "use strict";
    var AttachDocument = require('web.AttachDocument');
    var core = require('web.core');
    var _t = core._t;

    AttachDocument.include({
        _notifyInvalidFields: function (invalidFields) {
            var fields = this.state.fields;
            var warnings = invalidFields.map(function (fieldName) {
                var fieldStr = fields[fieldName].string;
                return _.str.sprintf('<li>%s</li>', _.escape(fieldStr));
            });
            warnings.unshift('<ul>');
            warnings.push('</ul>');
            this.do_warn(_t("The following fields are invalid:"), warnings.join(''), true);
         },

    });
});
