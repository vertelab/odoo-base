from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class IrModelField(models.Model):
    _inherit = 'ir.model.fields'
    
    def get_author(self):

        module_list = []

        for field in self:

            module_author = {
                "field_authors": set(),
                "field_modules": [],
                "field_record_id":field,
                "model_authors": set(),
                "model_modules": []
            }

            field_external_ids = self.env['ir.model.data'].search([('res_id','=',field.id),('model','=','ir.model.fields')])
            for field_external_id in field_external_ids:
                field_module = self.env['ir.module.module'].search([('name','=',field_external_id.module)])
                module_author["field_modules"].append(field_module.name) #name
                module_author["field_authors"].add(field_module.author) #author
            model_external_ids = self.env['ir.model.data'].search([('res_id','=',field.model_id.id),('model','=','ir.model')])
            for model_external_id in model_external_ids:
                model_module = self.env['ir.module.module'].search([('name','=',model_external_id.module)])
                module_author["model_modules"].append(model_module.name) #name
                module_author["model_authors"].add(model_module.author) #author
            module_list.append(module_author)

        relevant_moduls = list(filter(lambda x: not self.check_if_in(x),module_list))
        relevant_fields = [relevant_modul["field_record_id"] for relevant_modul in relevant_moduls]
        relevant_models = set([relevant_field.model_id for relevant_field in relevant_fields])
        return relevant_models

        raise UserError(f"{module_list=}")

    def create_mock(self):
        relevant_models = self.get_author()
        python_file = """from odoo import models, fields, api, _\n\n"""
        for relevant_model in relevant_models:
            python_file += f"class {self.fix_class_name(relevant_model)}({'models.Transient' if relevant_model.transient else 'models.Model'}):\n    _name='{relevant_model.model}'\n"
            for field in relevant_model.field_id: # Why does Odoo call a One2many field 'field_id' and not 'ids'?
                python_file += f"    {field.name} = fields.{field.ttype.replace(field.ttype[:1],field.ttype[:1].upper(),1)}({self.get_field_fuction_vals(field)})\n"
            python_file += "\n"

        with open("/usr/share/odoo-base/base_migration_helper/models/models_mock.py","w+",encoding='utf-8') as file:
            file.write(python_file)

        #raise UserError(f"{python_file=}")

    def get_field_fuction_vals(self,field):
        if field.ttype == "many2one" or field.ttype == "many2many":
            return f"comodel_name='{field.relation}'"
        elif field.ttype == "one2many":
            return f"comodel_name='{field.relation}',inverse_name='{field.relation_field}'"
        else:
            return ""

    def check_if_in(self,module):
        authors = ["OCA","Odoo S.A."]
        check_flag = False
        for author in authors:
            check_flag = True if author in module.get("field_authors") or author in module.get("model_authors") else False
        return check_flag

    def fix_class_name(self,model):
        name = ""
        name = model.name.replace(' ','')
        name = name.replace(name[:1],name[:1].upper())
        if "." in name:
            index = [i for i, char in enumerate(name) if char == "."]
            for count, i in enumerate(index):
                name = name.replace(name[i-count]+name[i+1-count],name[i+1-count].upper(),1)
        return name

