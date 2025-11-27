from odoo import api, fields, models, _


class SerpResult(models.Model):
    _name = 'serp.result'
    _description = 'SERP Result'
    _order = 'search_date desc'

    # partner_id = fields.Many2one(
    #     'res.partner',
    #     string='Partner',
    #     required=True,
    #     ondelete='cascade',
    #     index=True
    # )

    @api.model
    def _selection_target_model(self):
        return [(model.model, model.name) for model in self.env['ir.model'].sudo().search([])]

    @api.depends('res_model', 'res_id')
    def _compute_resource_ref(self):
        for wizard in self:
            if wizard.res_model and wizard.res_model in self.env:
                wizard.resource_ref = '%s,%s' % (wizard.res_model, wizard.res_id or 0)
            else:
                wizard.resource_ref = None

    res_model = fields.Char('Related Document Model', required=True, index=True)
    res_id = fields.Integer('Related Document ID', required=True, index=True)
    resource_ref = fields.Reference('_selection_target_model', 'Related Document', compute=_compute_resource_ref)

    # What was searched
    keyword = fields.Char(string='Keyword', required=True, index=True)
    domain = fields.Char(string='Domain')

    # Result
    position = fields.Integer(string='Position', required=True)
    url = fields.Char(string='URL')
    title = fields.Char(string='Title', help='Page title')
    snippet = fields.Text(string='Snippet', help='Preview text')

    # When and how
    search_date = fields.Datetime(string='Search Date', default=fields.Datetime.now, required=True)
    provider_id = fields.Many2one('serp.provider', string='Provider', ondelete='set null')

    # Search context
    country_code = fields.Char(string='Country')
    language = fields.Char(string='Language')
    search_engine = fields.Char(string='Search Engine')