odoo.define('af.KanbanController', function (require) {
"use strict";

/**
 * The KanbanController is the class that coordinates the kanban model and the
 * kanban renderer.  It also makes sure that update from the search view are
 * properly interpreted.
 */

var KanbanController = require('web.KanbanController');
var KanbanRecord = require('web.KanbanRecord');
var Context = require('web.Context');
var core = require('web.core');
var Domain = require('web.Domain');
var view_dialogs = require('web.view_dialogs');
var viewUtils = require('web.viewUtils');

var pyUtils = require('web.py_utils');

var _t = core._t;
var qweb = core.qweb;

KanbanRecord.include({
	_openRecord: function () {
        if (this.$el.hasClass('o_currently_dragged')) {
            // this record is currently being dragged and dropped, so we do not
            // want to open it.
            return;
        }
        console.log('KanbanRecord._openRecord');
        console.log(this);
        var editMode = this.$el.hasClass('oe_kanban_global_click_edit');
        var event = {
            id: this.db_id,
            mode: editMode ? 'edit' : 'readonly',
        };
        // Check if this is an advanced kanban
        var action_id = this.$el.data('kanban-adv-action-id');
        var action_func = this.$el.data('kanban-adv-action-func');        
        if (action_id || action_func) {
			if (action_id) {event.kadv_action_id = action_id};
			if (action_func) {event.kadv_action_func = action_func};
			var model = this.$el.data('kanban-adv-model');
			var domain = this.$el.data('kanban-adv-domain');
			var context = this.$el.data('kanban-adv-context');
			var action_context = this.$el.data('kanban-adv-action-context');
			var additional_context = this.$el.data('kanban-adv-additional-context');
			var target = this.$el.data('kanban-adv-target');
			if (model) {event.kadv_model = model};
			if (domain) {event.kadv_domain = domain};
			if (context) {event.kadv_context = context};
			if (action_context) {event.kadv_action_context = action_context};
			if (additional_context) {event.kadv_additional_context = additional_context};
			if (target) {event.kadv_target = target};
			event.kadv_res_id = this.id;
			// Looks like this is the record that is available when rendering the kanban
			event.kadv_record = this.record;
		};
        this.trigger_up('open_record', event);
    }
});

KanbanController.include({
    _onOpenRecord: function (event) {
		var self = this;
		console.log('ES IST LE OVERRIDDEN!');
		//~ console.log(this);
		console.log(event);
        event.stopPropagation();
        var record = this.model.get(event.data.id, {raw: true});
        //~ console.log(record);
        if (event.data.kadv_action_id || event.data.kadv_action_func){
			// This is an advanced kanban view.
			if (event.data.kadv_action_func){
				// Action is fetched by executing a python function
				var action;
				this._rpc({
					model: this.modelName,
					method: event.data.kadv_action_func,
					args: [
						event.data.kadv_res_id,
					],
					'params': {}
				})
				.done(function(result){
					console.log('done');
					console.log(result);
					var action = result;
					var additional_context = result.kadv_additional_context;
					if (event.data.kadv_additional_context){
						additional_context = pyUtils.eval(
							'context',
							event.data.kadv_additional_context,
							{record: event.data.kadv_record});
					}
					// This doesn't work for some reason. It looks like we're missing
					// a step where the returned action is converted in some way.
					// Check a regular button and follow the trail to find the magic.
					self.do_action(action, {'additional_context': additional_context});
				})
				.fail(function(result){
					//TODO: Better error handling
					alert('Something went horribly wrong in the advanced kanban!');
				})
			} else {
				// Action is a database or xml id
				//{'active_id': record.id.value, 'active_ids': [record.id.value], 'active_model': 'res.partner'}
				var action;
				var def = $.Deferred();
				this.trigger_up('load_action', {
					actionID: event.data.kadv_action_id,
					context: pyUtils.eval('context', event.data.kadv_action_context || '{}', {record: event.data.kadv_record}),
					on_success: def.resolve.bind(def),
				});
				def.done(function(result){
					console.log(arguments);
					var action = result;
					if (event.data.kadv_model){action.res_model = event.data.kadv_model;}
					if (event.data.kadv_target){action.target = event.data.kadv_target;}
					if (event.data.kadv_domain){
						action.domain = pyUtils.eval('context', event.data.kadv_domain, {record: event.data.kadv_record});
					}
					if (event.data.kadv_context){
						action.context = pyUtils.eval('context', event.data.kadv_context, {record: event.data.kadv_record});
					}
					//~ var additional_context = pyUtils.eval('context', event.data.kadv_additional_context || '{}', {record: event.data.kadv_record});
					var additional_context;
					if (event.data.kadv_additional_context) {
						additional_context = pyUtils.eval('context', event.data.kadv_additional_context || '{}', {record: event.data.kadv_record});
					} else {
						additional_context = {
							'active_id': event.data.kadv_res_id,
							'active_ids': [event.data.kadv_res_id],
							'active_model': self.modelName
						}
					}
					console.log('additional_context');
					console.log(event.data.kadv_additional_context);
					console.log(additional_context);
					// TODO: Figure out a way to build a default additional_context
					//~ {
						//~ 'active_id': 123,
						//~ 'active_ids': [123, 456, 789],
						//~ 'active_model': 'some.model.name'
					//~ }
					self.do_action(action, {'additional_context': additional_context});
				})
				.fail(function(result){
					//TODO: Better error handling
					alert('Something went horribly wrong in the advanced kanban!');
				})	
			}
			
			return;
		}
		// This is a normal kanban view
		return this._super.apply(this, arguments);
        //~ this.trigger_up('switch_view', {
            //~ view_type: 'form',
            //~ res_id: record.res_id,
            //~ mode: event.data.mode || 'readonly',
            //~ model: this.modelName,
        //~ });
    }
});

return KanbanController;

});


//~ var additional_context;
					//~ if (event.data.kadv_additional_context) {
						//~ additional_context = pyUtils.eval('context', event.data.kadv_additional_context || '{}', {record: event.data.kadv_record});
					//~ } else {
						//~ additional_context = {
							//~ 'active_id': event.data.kadv_res_id,
							//~ 'active_ids': [event.data.kadv_res_id],
							//~ 'active_model': this.modelName
						//~ }
					//~ }
