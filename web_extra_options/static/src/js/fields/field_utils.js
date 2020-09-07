odoo.define('web_extra_options.field_utils', function (require) {
"use strict";

var field_utils = require('web.field_utils');
var session = require('web.session');
var time = require('web.time');

/**
 * Returns a string representing a date.  If the value is false, then we return
 * an empty string. Note that this is dependant on the localization settings
 *
 * @param {Moment|false} value
 * @param {Object} [field]
 *        a description of the field (note: this parameter is ignored)
 * @param {Object} [options] additional options
 * @param {boolean} [options.timezone=true] use the user timezone when formating the
 *        date
 * @returns {string}
 */
function formatDate(value, field, options) {
    if (value === false) {
        return "";
    }
    if (field && field.type === 'datetime') {
        if (!options || !('timezone' in options) || options.timezone) {
            value = value.clone().add(session.getTZOffset(value), 'minutes');
        }
    }
    // Fetch format from datepicker options
    var format = options && options.datepicker && options.datepicker.format;
    // Fallback to original behaviour
    format = format ? format : time.getLangDateFormat();
    return value.format(format);
}

/**
 * Returns a string representing a datetime.  If the value is false, then we
 * return an empty string.  Note that this is dependant on the localization
 * settings
 *
 * @params {Moment|false}
 * @param {Object} [field]
 *        a description of the field (note: this parameter is ignored)
 * @param {Object} [options] additional options
 * @param {boolean} [options.timezone=true] use the user timezone when formating the
 *        dateformatDateTime
 * @returns {string}
 */
function formatDateTime(value, field, options) {
    if (value === false) {
        return "";
    }
    if (!options || !('timezone' in options) || options.timezone) {
        value = value.clone().add(session.getTZOffset(value), 'minutes');
    }

    // Fetch format from datepicker options
    let format;
    let hide;
    if (options && options.datepicker) {
        format = options.datepicker.format;
        hide = options.datepicker.hide;
    }
    // Fallback to original method
    format = format ? format : time.getLangDatetimeFormat();
    // TODO: This feature does not affect edit mode. Implement this for web.datepicker JS module.
    if (hide) {
        if (hide.seconds) {
            format = format.replaceAll(/:?[sS]+/g, '');
        }
    }
    return value.format(format);
}

field_utils.format.datetime = formatDateTime;
field_utils.format.date = formatDate;

return {format: { datetime: formatDateTime}};
});
