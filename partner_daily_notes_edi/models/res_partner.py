from odoo import models, fields, api, _


class ResPartnerNotes(models.Model):
    _inherit = 'res.partner.notes'

    route_id = fields.Many2one(comodel_name="edi.route")
    
    @api.multi
    def _edi_message_create(self):
        for note in self:
            vals = {
                'name': 'set contact msg',
                'edi_type': env.ref('edi_af_as.asok_contact').id,
                'model': note._name,
                'res_id': note.id,
                'route_id': self.env.ref('edi_af_as.asok_contact_route').id,
                'route_type': 'edi_af_as_contact',
            }
            message = self.env['edi.message'].create(vals)
            message.pack()
            route.run()

    @api.model
    def create(self, values):
        """
        Trigger new notes and creates edi-messages for them
        """
        rec = super(ResPartnerNotes,self).create(values)
        rec._edi_message_create()
        return rec
