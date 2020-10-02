from odoo import models, fields, api, _


class ResPartnerNotes(models.Model):
    _inherit = 'res.partner.notes'

    route_id = fields.Many2one(comodel_name="edi.route")
    
    @api.multi
    def _edi_message_create(self, edi_type, check_double=False):
        for note in self:
            self.env['edi.message']._edi_message_create(
                edi_type=edi_type,
                obj=note,
                route=note.route_id,
                check_double=check_double)

    @api.model
    def create(self, values):
        """
        Trigger new notes and creates edi-messages for them
        """
        rec = super(ResPartnerNotes,self).create(values)
        rec._edi_message_create('edi_af_as_notes_post')
        return rec
