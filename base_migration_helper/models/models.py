from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class IrModelField(models.Model):
    _inherit = 'ir.model.fields'
    
    def get_author(self):
        for field in self:

            field_authors = ""
            field_modules = ""
            field_external_ids = self.env['ir.model.data'].search([('res_id','=',field.id),('model','=','ir.model.fields')])
            for field_external_id in field_external_ids:
                field_module = self.env['ir.module.module'].search([('name','=',field_external_id.module)])
                field_modules += ","+field_module.name
                field_authors += ","+field_module.author

            model_authors = ""
            model_modules = ""
            model_external_ids = self.env['ir.model.data'].search([('res_id','=',field.model_id.id),('model','=','ir.model')])
            for model_external_id in model_external_ids:
                model_module = self.env['ir.module.module'].search([('name','=',model_external_id.module)])
                model_modules += ","+model_module.name
                model_authors += ","+model_module.author
            #field.field_authors = field_authors
            #field.model_authors = model_modules
            #raise UserError(f"{field_modules=} {field_authors=} {model_modules=} {model_authors=}")