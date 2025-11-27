from odoo import api, fields, models, _

class SerpKeyword(models.Model):
    _name = 'serp.keyword'
    _description = 'SERP Keyword'

    name = fields.Char(string='Keyword', required=True)

    _sql_constraints = [
        ('unique_keyword', 'unique(name)', 'Keyword already exists!')
    ]