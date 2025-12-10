# models/serp_keyword.py
from odoo import api, fields, models, _


class SerpKeyword(models.Model):
    _name = 'serp.keyword'
    _description = 'SERP Keyword'
    _order = 'keyword'

    keyword = fields.Char(string='Keyword', required=True)
    partner_id = fields.Many2one('res.partner', string='Partner', ondelete='cascade', index=True)
    country_id = fields.Many2one('res.country', string='Country')
    language_id = fields.Many2one('res.lang', string='Language')

    _sql_constraints = [
        ('unique_keyword_partner',
         'unique(keyword, partner_id, country_id, language_id)',
         'This keyword already exists for this partner!')
    ]