from odoo import models, fields, api, _
import logging
from odoo.osv import expression

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def set_all_customers_number(self):
        partners = self.env['res.partner'].search([])
        _logger.warning(f"{partners=}")
        partners._set_costumer_number()

    def _set_costumer_number(self):
        for rec in self:
            if not rec.customer_sequence:
                sequence_code = self.env['ir.sequence'].next_by_code('res.partner')
                partner_id = self.env['res.partner'].search([('customer_sequence', '=', sequence_code)], limit=1)
                while partner_id:
                    sequence_code = self.env['ir.sequence'].next_by_code('res.partner')
                    partner_id = self.env['res.partner'].search([('customer_sequence', '=', sequence_code)], limit=1)
                rec.customer_sequence = sequence_code

    customer_sequence = fields.Char(string='Customer Number', readonly=True)
    our_customer_number = fields.Integer(string='Our Customer Number')
    company_code_partner = fields.Char(string='Legal Unit')

    @api.model
    def create(self, values):
        res = super(ResPartner, self).create(values)
        res._set_costumer_number()
        return res

    # ~ def name_get(self):
        # ~ _logger.warning("name_get"*10)
        # ~ res = super(ResPartner, self).name_get()
        # ~ _logger.warning(f"{res=}")
        # ~ result = []
        # ~ for record in self:
            # ~ result.append((record.id, "{} ({})".format(record.name, record.type)))
        # ~ _logger.warning(f"{result=}")
        # ~ return result


    # ~ def name_get(self):
        # ~ res = []
        # ~ for partner in self:
            # ~ name = partner._get_name()
            # ~ res.append((partner.id, name))
        # ~ return res


    def _get_name(self):
        """ Utility method to allow name_get to be overrided without re-browse the partner """
        partner = self
        name = partner.name or ''
        _logger.warning(f"{name=}")
        if name and partner.type in ['invoice', 'delivery', 'other']:
           name = partner.name + " " + dict(self.fields_get(['type'])['type']['selection'])[partner.type]
           _logger.warning(f"{name=}")
        
        if partner.company_name or partner.parent_id:
            if not name and partner.type in ['invoice', 'delivery', 'other']:
                name = dict(self.fields_get(['type'])['type']['selection'])[partner.type]
            if not partner.is_company:
                name = self._get_contact_name(partner, name)
        if self._context.get('show_address_only'):
            name = partner._display_address(without_company=True)
        if self._context.get('show_address'):
            name = name + "\n" + partner._display_address(without_company=True)
        name = name.replace('\n\n', '\n')
        name = name.replace('\n\n', '\n')
        if self._context.get('address_inline'):
            splitted_names = name.split("\n")
            name = ", ".join([n for n in splitted_names if n.strip()])
        if self._context.get('show_email') and partner.email:
            name = "%s <%s>" % (name, partner.email)
        if self._context.get('html_format'):
            name = name.replace('\n', '<br/>')
        if self._context.get('show_vat') and partner.vat:
            name = "%s ‒ %s" % (name, partner.vat)

        return name 
