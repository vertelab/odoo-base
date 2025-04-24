from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class IrModel(models.Model):
    _inherit = 'ir.model'
    
    def create_mock(self, model_meta_datas):
        python_file = """from odoo import models, fields, api, _\n\n"""
        for model in model_meta_datas:
            _logger.warning(f"{model=}")
            python_file += f"\n\n"
            python_file += f"class {model['model_model'].replace('.','DOT')}({'models.Model' if not model['model_record'].transient else 'models.TransientModel'}):\n"
            _logger.warning(f"{python_file=}")
            python_file += f"    {'_inherit' if model['should_inherit'] else '_name'} = '{model['model_model']}'\n"
            python_file += f"\n"
            _logger.warning(f"{python_file=}")
            # Field Generation
            for field in model['model_fields']:
                field_str = self._generate_field_syntax(field)
                python_file += f"    {field_str}\n"
        
        python_file += "\n"
        _logger.warning(f"{python_file=}")

        with open("/usr/share/odoo-base/base_migration_helper/models/models_mock_test.py","w+",encoding='utf-8') as file:
            file.write(python_file)
    
    def _generate_field_syntax(self, field):
        """Generate proper Odoo field syntax"""
        field_type = field['ttype']
        params = []
        
        # Required Parameters
        if field['field_description']:
            params.append(f"string='{field['field_description']}'")
        
        # Type-Specific Parameters
        if field_type in ('many2one', 'many2many', 'one2many'):
            params.append(f"comodel_name='{field['relation']}'")
            if field_type == 'one2many':
                params.append(f"inverse_name='{field['relation_field']}'")
        
        # Common Parameters
        if field['readonly']:
            params.append("readonly=True")
        if not field['store']:
            params.append("store=False")
        
        # Selection Field Handling
        if field_type == 'selection':
            if field['selection_ids']:
                selection_items = []
                for item in field['selection_ids']:
                    selection_items.append(f"('{item.value}', '{item.name}')")
                params.append(f"selection=[{','.join(selection_items)}]")
            else:
                params.append("selection=[]")
        
        return f"{field['name']} = fields.{field_type.capitalize()}({', '.join(params)}) #Source Module {field['module']}, Module author {field['author']}"
    
    
    def loop_on_model(self):
        model_meta_datas = []
        for model in self:
            model_meta_datas.append(model.meta_data_module())
        model.create_mock(model_meta_datas)
        
    def meta_data_module(self):
        module_meta = {}
        model_external_id = self.env['ir.model.data'].search(
            [('res_id', '=', self.id),('model', '=', 'ir.model'),('module','!=','base_migration_helper')],
            order='create_date asc',
            limit=1
        )
        model_module = self.env['ir.module.module'].search([('name','=',model_external_id.module)])
        module_meta["module_record"] = model_module
        module_meta["model_record"] = self
        module_meta["model_name"] = self.name
        module_meta["model_model"] = self.model
        module_meta["model_source_module"] = model_module.name
        module_meta["model_source_author"] = model_module.author
        module_meta["should_inherit"] = False
        if model_module.author == "Odoo S.A" or model_module.author == "Odoo S.A." or "OCA" in model_module.author:
           module_meta["should_inherit"] = True
        module_meta["model_fields"] = self.meta_data_field()
        return module_meta
        
    def meta_data_field(self):
        field_metadata = []
        for field in self.field_id:
            field_external_id = self.env['ir.model.data'].search(
                [('res_id', '=', field.id),('model', '=', 'ir.model.fields'),('module','!=','base_migration_helper')],
                order='create_date asc',
                limit=1
            )
            field_module = self.env['ir.module.module'].search([('name','=',field_external_id.module)])
            skip_field = False
            if field_module.author == "Odoo S.A" or field_module.author == "Odoo S.A." or "OCA" in field_module.author:
               skip_field = True
            if not skip_field:
               field_metadata.append(
               {
                   "field_record":field,
                   "name":field.name,
                   "field_description":field.field_description,
                   "model":field.model,
                   "ttype":field.ttype,
                   "store":field.store,
                   "readonly":field.readonly,
                   "relation":field.relation,
                   "relation_field":field.relation_field,
                   "selection_ids":field.selection_ids,
                   "author":field_module.author,
                   "module":field_module.name,
               }
            )
        return field_metadata



