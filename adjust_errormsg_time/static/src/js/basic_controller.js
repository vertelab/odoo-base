odoo.define('adjust_errormsg_time.BasicController', function (require) {
    "use strict";
    var BasicController = require('web.BasicController');
    var core = require('web.core');
    var _t = core._t;
	
    BasicController.include({
        _notifyInvalidFields: function (invalidFields) {
            var record = this.model.get(this.handle, {raw: true});
            var fields = record.fields;
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
