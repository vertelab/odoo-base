from odoo import api, fields, models, _

class SerpKeyword(models.Model):
    _name = 'serp.keyword'
    _description = 'SERP Keyword'

    name = fields.Char(string='Keyword', required=True)
    serp_last_check = fields.Datetime(
        string='Last SERP Check',
        readonly=True
    )

    _sql_constraints = [
        ('unique_keyword', 'unique(name)', 'Keyword already exists!')
    ]