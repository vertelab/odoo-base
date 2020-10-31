from odoo import models, fields, api, _


class ResPartnerNotes(models.Model):
    _inherit = 'res.partner.notes'

    route_id = fields.Many2one(comodel_name="edi.route")
    
    @api.multi
    def _edi_message_create(self):
        for note in self:
            route = self.env['edi.route'].sudo().search([('id', '=', self.env['ir.model.data'].xmlid_to_res_id('edi_af_as_notes.asok_note_post_route'))])
            vals = {
                'name': 'set contact msg',
                'edi_type': self.env.ref('edi_af_as_notes.edi_af_as_notes_post').id,
                'model': note._name,
                'res_id': note.id,
                'route_id': self.env.ref('edi_af_as_notes.asok_note_post_route').id,
                'route_type': 'edi_af_as_notes_post',
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
