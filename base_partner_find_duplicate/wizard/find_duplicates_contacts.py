from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging

class res_partner_find_duplicates(models.TransientModel):
    _name = "find.duplicates.contacts.wizard"
    _description = "Find duplicates of contact information"
    find_duplicates_filter = fields.Selection([('name', 'Name'), ('email', 'Email'), ('phone', 'Phone')], required=True)

    def find_duplicates(self):

        # Group partners based on the selected field
        grouped_partners = {}

        #logging.warning(f"{self.env['res.partner'].search([])}")

        for contact_info in self.env['res.partner'].search([(self.find_duplicates_filter, '!=', False),(self.find_duplicates_filter, '!=', '')]):
            
            # key = contact_info[filter], i.e: contact_info['name'] = 'Abigail Peterson' <-- Key
            key = contact_info[self.find_duplicates_filter]

            #logging.warning(key)

            # If 'Abigail Peterson' is not in the grouped_partners 
            if key not in grouped_partners:
                # Add 'Abigail Peterson' to the dictionary 'grouped_partners' as a new element
                grouped_partners[key] = [contact_info.id]
            else:
                # If 'Abigail Peterson' already is existing in the dictionary, just add another value to the already existing element
                grouped_partners[key].append(contact_info.id)

        # Find duplicates from the 
        duplicates_ids = []

        for key in grouped_partners:
            if len(grouped_partners[key]) > 1:
                duplicates_ids += grouped_partners[key]
                #logging.warning(f"{grouped_partners[key]=}")

        logging.warning(duplicates_ids)

        return {
            'name' : 'Search Result',
            'view_mode': 'tree,form',
            'res_model': "res.partner",
            #'res_id': self.id,
            'domain':[('id', 'in', duplicates_ids)],
            'target': "current",
            'type': 'ir.actions.act_window',
            'context': {'group_by': self.find_duplicates_filter}, 
        }
