odoo.define('html_field_code_view.field.html', function (require) {
    'use strict';

    var config = require('web.config');

    var FieldHtml = require('web_editor.field.html');


    FieldHtml.include({
        commitChanges: function () {
            var self = this;
            if (config.isDebug() && this.mode === 'edit') {
                var layoutInfo = $.summernote.core.dom.makeLayoutInfo(this.wysiwyg.$editor);
                $.summernote.pluginEvents.codeview(undefined, undefined, layoutInfo, false);
            }
            if (this.mode == "readonly" || !this.isRendered) {
                return this._super();
            }
            var _super = this._super.bind(this);
            return this.wysiwyg.saveModifiedImages(this.$content).then(function () {
                return self.wysiwyg.save(self.nodeOptions).then(function (result) {
                    self._isDirty = result.isDirty;
                    _super();
                });
            });
        },

        _getWysiwygOptions: function () {
            var self = this;
            return Object.assign({}, this.nodeOptions, {
                recordInfo: {
                    context: this.record.getContext(this.recordParams),
                    res_model: this.model,
                    res_id: this.res_id,
                },
                noAttachment: this.nodeOptions['no-attachment'],
                inIframe: !!this.nodeOptions.cssEdit,
                iframeCssAssets: this.nodeOptions.cssEdit,
                snippets: this.nodeOptions.snippets,

                tabsize: 0,
                height: 180,
                generateOptions: function (options) {
                    var toolbar = options.toolbar || options.airPopover || {};
                    var para = _.find(toolbar, function (item) {
                        return item[0] === 'para';
                    });
                    if (para && para[1] && para[1].indexOf('checklist') === -1) {
                        para[1].splice(2, 0, 'checklist');
                    }

                    options.codeview = true;
                    var view = _.find(toolbar, function (item) {
                        return item[0] === 'view';
                    });
                    if (view) {
                        if (!view[1].includes('codeview')) {
                            view[1].splice(-1, 0, 'codeview');
                        }
                    } else {
                        toolbar.splice(-1, 0, ['view', ['codeview']]);
                    }

                    if (self.model === "mail.compose.message" || self.model === "mailing.mailing") {
                        options.noVideos = true;
                    }
                    options.prettifyHtml = false;
                    return options;
                },
            });
        },
    })

});
