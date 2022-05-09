import logging

from odoo import models, fields, api, _
import base64
import xml.etree.cElementTree as ET
from fnmatch import fnmatch

_logger = logging.getLogger(__name__)


class XMLExport(models.TransientModel):
    _name = 'xml.export'

    active_model = fields.Char()
    active_id = fields.Integer()
    attachment_name = fields.Char()

    def generate_xml_record(self, model_records, records, ir_model_id, names):
        record = ET.SubElement(records, "record")
        excluded_fields = ['create_date', 'message_ids', 'id', 'write_date', 'create_uid', '__last_update',
                           'write_uid', 'active', 'my_activity_date_deadline', 'resource_id',
                           'resource_calendar_id', 'last_activity', 'last_activity_time']
        excluded_fields += [field.name for field in ir_model_id.field_id
                            if field.name.startswith('activity_') or field.name.startswith('message_')
                            ]
        for field in ir_model_id.field_id:
            if field.name not in excluded_fields + names:
                if field.ttype in ['boolean', 'char', 'text', 'float', 'integer', 'selection', 'date', 'datetime']:
                    try:
                        ET.SubElement(record, 'field', name=field.name).text = str(model_records[field.name])
                    except:
                        pass
                elif field.ttype in ['many2one']:
                    if model_records[field.name]:
                        keys, values = zip(*model_records[field.name].get_external_id().items()) \
                                           if model_records[field.name].get_external_id() \
                                           else 0, "%s-%s" % (model_records[field.name]._name,
                                                              model_records[field.name].id)
                        if values == "":
                            values = "%s-%s" % (model_records[field.name]._name, model_records[field.name].id)
                        #
                        ET.SubElement(record, 'field', name=field.name, ref="%s" % values)

                elif field.ttype in ['many2many']:
                    mtomvalues = []
                    for val in model_records[field.name]:
                        key, values = 0, '' if not val.get_external_id() else val.get_external_id().items()
                        if len(values) > 0:
                            mtomvalues.append("(4, ref('%s'))" % list(values)[0][1])
                    if len(mtomvalues) > 0:
                        ET.SubElement(record, 'field', name=field.name, eval="[%s]" % (','.join(mtomvalues)))
        return record

    def generate_xml(self):
        active_model = self.active_model or self._context['active_model']
        active_id = self.active_id or self._context['active_ids']

        ir_model_id = self.env['ir.model'].search([('model', '=', active_model)])
        model_id = self.env[active_model].browse(active_id)

        xml = ET.Element('xml', encoding="utf-8", version="1.0")
        root = ET.SubElement(xml, "root")
        records = ET.SubElement(root, "records")

        names = [name for name in model_id.fields_get().keys() if fnmatch(name, 'in_group*')] + \
                [name for name in model_id.fields_get().keys() if fnmatch(name, 'sel_groups*')]
        for model_records in model_id:
            self.generate_xml_record(model_records, records, ir_model_id, names)

        return xml

    def create_attachment(self):
        active_model = self.active_model or self._context['active_model']
        ir_model_id = self.env['ir.model'].search([('model', '=', active_model)])

        xml = self.generate_xml()
        xmlstr = ET.tostring(xml)

        attachment_create = {
            'name': str(ir_model_id.name) + '.xml',
            'datas': base64.encodebytes(xmlstr),
            'mimetype': 'application/xml',
        }

        if self.attachment_name:
            attachment_create["res_model"] = active_model
            attachment_create["res_id"] = self.active_id or self._context["active_ids"]
            attachment_create["name"] = self.attachment_name

        return self.env['ir.attachment'].create(attachment_create)

    def download_xml_export(self):
        attachment = self.create_attachment()
        simplified_form_view = self.env.ref("record_export_to_xml.view_attachment_simplified_form")

        action = {
            "name": _("Export Record"),
            "view_mode": "form",
            "view_id": simplified_form_view.id,
            "res_model": "ir.attachment",
            "type": "ir.actions.act_window",
            "target": "new",
            "res_id": attachment.id,
        }

        return action

