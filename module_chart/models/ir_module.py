from odoo import fields, models, api


class Module(models.Model):
    _inherit = 'ir.module.module'

    @api.multi
    def get_module_graph(self):
        nodes = []
        edges = []
        for module in self:
            nodes.append({'id': module.id, 'label': module.name, 'state': module.state})
            # dependency
            for dependency in module.dependencies_id:
                depended_module = dependency.depend_id
                nodes.append({'id': depended_module.id, 'label': depended_module.name, 'state': depended_module.state})
                edges.append({'from': module.id, 'to': depended_module.id})
                if depended_module.dependencies_id:
                    res = depended_module.get_module_graph()
                    nodes.extend(res['nodes'])
                    edges.extend(res['edges'])

            # exclusion
            for exclusion in module.exclusion_ids:
                excluded_module = exclusion.exclusion_id
                nodes.append({'id': excluded_module.id, 'label': excluded_module.name, 'state': excluded_module.state})
                edges.append({'from': module.id, 'to': excluded_module.id, 'type': 'exclusion'})
                if excluded_module.dependencies_id:
                    res = excluded_module.get_module_graph()
                    nodes.extend(res['nodes'])
                    edges.extend(res['edges'])

        unique_nodes = list({node['id']: node for node in nodes}.values())
        unique_edges = list({'%s-%s' % (edge['from'], edge['to']): edge for edge in edges}.values())
        return {'nodes': unique_nodes, 'edges': unique_edges}




