(function() {

var instance = openerp;
var QWeb = instance.web.qweb,
    _t = instance.web._t;
    
instance.web.ViewManagerAction = instance.web.ViewManagerAction.extend({
    
    on_debug_changed: function (evt) {
        var self = this,
            $sel = $(evt.currentTarget),
            $option = $sel.find('option:selected'),
            val = $sel.val(),
            current_view = this.views[this.active_view].controller;
        if (val == 'profile_model') {
            var ids = current_view.get_selected_ids();
            if (ids.length === 1) {
                new openerp.Model('profile.model').call('profile', [this.dataset.model, ids[0]]).then(
                    function (result) {
                        console.log(result);
                        self.do_action(result);
                });
            };
        }
        else {
            this._super(evt);
        }
    }
})
})();
