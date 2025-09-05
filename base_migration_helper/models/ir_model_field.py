from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class IrModel(models.Model):
    _inherit = 'ir.model'

    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
    
    def create_mock(self, model_meta_datas):
        reference_selection ="""
    @api.model
    def _selection_target_model_mock(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]
        """
        python_file = """from odoo import models, fields, api, _\n\n"""
        depends = []
        for model in model_meta_datas:
            is_abstract = self.env[model['model_model']]._abstract
            is_transient = model['model_record'].transient
            _logger.warning(f"{is_abstract=}")
            #_logger.warning(f"{self.env['abstract.dms.mixin']._abstract=}")
            #_logger.warning(f"{self.env[model['model_model']]}")
            python_file += f"\n\n"

            model_type = 'models.Model'
            if is_abstract:
                model_type = 'models.AbstractModel'
            elif is_transient:
                model_type = 'models.TransientModel'

            python_file += f"class {model['model_model'].replace('.','DOT')}({model_type}):\n"
            #_logger.warning(f"{python_file=}")
            python_file += f"    {'_inherit' if model['should_inherit'] else '_name'} = '{model['model_model']}'\n"
            python_file += reference_selection 
            python_file += f"\n"
            #_logger.warning(f"{python_file=}")
            # Field Generation
            skip_fields =["create_date",
                "create_uid",
                "write_date",
                "write_uid",
                "__last_update"
            ]
            for field in model['model_fields']:
                if field['name'] not in skip_fields:
                    field_str = self._generate_field_syntax(field)
                    python_file += f"    {field_str}\n"

            if model['should_inherit']:
                depends.append(model['model_source_module'])
            #else:
            #    for m in model['module_record'].dependencies_id:
            #        depends.append(m.name)
            depends = list(set(depends))

            _logger.warning(f"{depends=}")
            
               
        
        python_file += "\n"
        #_logger.warning(f"{python_file=}")

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
            if field_type == 'one2many' and field['relation_field']:
                params.append(f"inverse_name='{field['relation_field']}'")
        if field_type == "reference":
            params.append(f"selection='_selection_target_model_mock'")
        if field['related']:
            params.append(f"related='{field['related']}'")
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
        if field_type == "many2one_reference":
            field_formated = "Many2oneReference"
        else:
            field_formated = field_type.capitalize()
        return f"{field['name']} = fields.{field_formated}({', '.join(params)}) #Source Module {field['module']}, Module author {field['author']}"
    
    
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
        _logger.warning(f"{model_external_id=}")
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
            _logger.warning(f"{field=}")
            field_external_id = self.env['ir.model.data'].search(
                [('res_id', '=', field.id),('model', '=', 'ir.model.fields'),('module','!=','base_migration_helper')],
                order='create_date asc',
                limit=1
            )
            skip_field = False
            field_module = False
            if field_external_id:
                field_module = self.env['ir.module.module'].search([('name','=',field_external_id.module)])
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
                   "related":field.related,
                   "selection_ids":field.selection_ids,
                   "author":field_module.author if field_module.author else "Missing author",
                   "module":field_module.name if field_module.name else "Missing module",
               }
            )
        return field_metadata



