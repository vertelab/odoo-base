odoo.define('module_chart.graph', function (require) {
    "use strict";

    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var QWeb = core.qweb;

    var STATE_COLOR = {
        'uninstallable': '#eaeaa4',
        'installed': '#97c2fc',
        'uninstalled': '#e5f8fc',
        'to install': '#939afc',
        'to upgrade': '#AEFCAB',
        'to remove': '#fcadb7',
    };

    var ModuleGraph = AbstractAction.extend({
        template: 'ModuleGraph',
        events: {
            'click .module_graph_nav li': '_onClickNavModule',
            'keyup input': '_onInputKeyup',
        },

        init: function () {
            var res = this._super.apply(this, arguments);
            this.module_info = {};
            this.nodes = [];
            this.edges = [];
            this.graph_nodes = new vis.DataSet([]);
            this.graph_edges = new vis.DataSet([]);
            this.graph_data = {
                nodes: this.graph_nodes,
                edges: this.graph_edges
            };
            this.graph_options = {
                edges: {
                    arrows: 'to',
                }
            };
            return res;
        },

        start: function () {
            var self = this;
            rpc.query({
                model: 'ir.module.module',
                method: 'search_read',
                fields: ['id', 'name', 'shortdesc', 'state'],
                order: 'shortdesc'
            }).then(function (data) {
                data.forEach(function (node) {
                    self.nodes.push({'id': node.id, 'label': node.name, 'state': node.state, 'shortdesc': node.shortdesc});
                });

                self.$el.html(QWeb.render("ModuleGraph", {widget: self}));
                var container = self.$('.module_graph').get()[0];
                self.network = new vis.Network(container, self.graph_data, self.graph_options);

                // network handlers
                self.network.on("doubleClick", function (params) {
                    var module_id = params['nodes'][0];
                    if (module_id) {
                        self._onClickModuleInfo(module_id);
                    }
                });

                self.network.on("oncontext", function (params) {
                    params['event'].preventDefault();
                    params['event'].stopPropagation();
                    var node_id = params['nodes'][0];
                    if (node_id) {
                        self.graph_nodes.remove(node_id);
                        self.$(`li[data-id="${node_id}"]`).removeClass('module_selected');
                    }
                });
            });
            return this._super.apply(this, arguments);
        },

        _onInputKeyup: function () {
            var filter = this.$el.find('input').val().toUpperCase();
            var li = this.$el.find('.module_graph_nav_list li');

            for (var i = 0; i < li.length; i++) {
                var txtValue = li[i].textContent || li[i].innerText;
                if (txtValue.toUpperCase().indexOf(filter) === -1) {
                    li[i].style.display = 'none';
                } else {
                    li[i].style.display = '';
                }
            }
        },

        _onClickModuleInfo: function (module_id) {
            this.do_action({
                type: 'ir.actions.act_window',
                view_type: 'form',
                view_mode: 'form',
                views: [[false, 'form']],
                target: 'new',
                res_model: 'ir.module.module',
                res_id: module_id,
            });
        },

        _onClickNavModule: function (event) {
            var self = this;
            if (event.target.getAttribute('data-id') && event.target.className !== 'module_selected') {
                this.graph_nodes.update([{
                    id: Number(event.target.getAttribute('data-id')),
                    label: event.target.getAttribute('data-label')
                }]);

                rpc.query({
                    model: 'ir.module.module',
                    method: 'get_module_graph',
                    args: [Number(event.target.getAttribute('data-id'))],
                }).then(function (data) {
                    var nodes = [];
                    var edges = [];
                    data['nodes'].forEach(function (node) {
                        if (node['id']) {
                            nodes.push({'id': node['id'], 'label': node['label'], 'color': {'background': STATE_COLOR[node['state']], 'state': node['state']}});
                            self.$(`li[data-id="${node['id']}"]`).addClass('module_selected');
                        }
                    });
                    self.graph_nodes.update(nodes);

                    data['edges'].forEach(function (edge) {
                        if (self.edges.filter(e => e.from === edge['from'] && e.to === edge['to']).length === 0) {
                            var new_edge = {'from': edge['from'], 'to': edge['to']};
                            if (edge['type'] === 'exclusion') {
                                new_edge['color'] = {'color': 'red', 'highlight': 'red'}
                            }
                            self.edges.push(new_edge);
                            edges.push(new_edge);
                        }
                    });
                    self.graph_edges.update(edges);
                })
            }
        },
    });

    core.action_registry.add('module_graph', ModuleGraph);
    return ModuleGraph;
});