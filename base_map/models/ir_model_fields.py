# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution, third party addon
#    Copyright (C) 2004-2019 Vertel AB (<http://vertel.se>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)

class IrModelFields(models.Model):
    _inherit = 'ir.model.fields'

    map_id = fields.One2many(comodel_name='ir.model.fields.mapping', inverse_name='odoo_field', string='Mapped line id', copy=False)
    map_system = fields.Char(string='Mapped system', related='map_id.target_system', help="The name of the mapped system")
    map_table = fields.Char(string='Mapped system table', related='map_id.target_table', help="The name of the table in the mapped system")
    map_field = fields.Char(string='Mapped system field', related='map_id.target_field', help="The name of the field in the mapped system")
    map_odoo_master = fields.Boolean(string='Odoo master', related='map_id.odoo_master', help="Is Odoo master of the data?")
    map_type = fields.Char(string='Mapped type', related='map_id.target_type', help="The type of the mapped system field")
    map_comment = fields.Char(string='Comment', related='map_id.comment', help="Comment regarding the mapping")

    def create_mapped_field(self):
        vals = {
            'odoo_field' : self.id,
        }

        self.env['ir.model.fields.mapping'].create(vals)

    @api.multi
    def write(self, values):

        new_values = {}
        res = False

        # catch wrties to these fileds and send them over to ir.model.fields.mapping instead
        for field in ['map_id','map_system','map_table','map_field','map_odoo_master','map_type','map_comment']:
            if field in values:
                
                # self.fields_get([field], ['related'])[field]['related'][1]
                # This code fetches the related field for 'field'

                new_values[self.fields_get([field], ['related'])[field]['related'][1]] = values.pop(field)

        # check if we have values to send to ir.model.fields.mapping
        if new_values:
            # try to find field_mapping
            field_mapping = self.env['ir.model.fields.mapping'].search([('odoo_field','=',self.id)], limit=1)

            if field_mapping:
                # Update if field_mapping already exists
                field_mapping.write(new_values)
            else:
                # Create new field_mapping if none exists
                new_values['odoo_field'] = self.id
                self.env['ir.model.fields.mapping'].create(new_values)

            res = True

        if values:
            # If we have writes to the standard ir.model.fields, call super write
            res = super(IrModelFields, self).write(values)

        return res

class IrModelFieldsMapping(models.Model):
    _name = 'ir.model.fields.mapping'
    _description = 'Helper model to ir.model.fields'
    
    odoo_field = fields.Many2one(comodel_name='ir.model.fields', string='Odoo Field', help="The mapped Odoo field", copy=False)
    odoo_master = fields.Boolean(string='Odoo master', help="Is Odoo master of the data?")
    target_system = fields.Char(string='Mapped system', help="The name of the mapped system")
    target_table = fields.Char(string='Mapped system table', help="The name of the table in the mapped system")
    target_field = fields.Char(string='Mapped system field', help="The name of the field in the mapped system")
    target_type = fields.Char(string='Mapped type', help="The type of the mapped system field")
    comment = fields.Char(string='Comment', help="Comment regarding the mapping")

    _sql_constraints = [
                    ('field_unique', 
                     'unique(odoo_field)',
                     'This Odoo field has already been mapped!')
    ]

    def write(self, values):
        res = super(IrModelFieldsMapping, self).write(values)
        return res

    def create(self, values):
        res = super(IrModelFieldsMapping, self).create(values)
        
        # This is probably not needed anymore.
        # ext_vals = {
        #     'module': 'base_map',s
        #     'model' : 'ir.model.fields.mapping',
        #     'name' : 'base_map_%s' % res.id,
        #     'res_id' : res.id,
        # }
        # self.env['ir.model.data'].create(ext_vals)

        return res