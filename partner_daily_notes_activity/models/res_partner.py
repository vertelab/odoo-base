from odoo import models, fields, api, _


class res_partner(models.Model):
    _inherit = 'res.partner'

    next_event_count = fields.Integer(string="Next Event", compute='daily_note_record')
    next_contact = fields.Date(string="Next Contact", compute='daily_note_record')
    last_contact = fields.Date(string="Last Contact", compute='daily_note_record')

    @api.depends('name')
    def daily_note_record(self):
        for rec in self:
            if rec.id:
                daily_note_counter = rec.env['res.partner.notes'].search_count([
                    ('partner_id', '=', rec.id), ('note_date', '>', fields.Date.today())])
                rec.next_event_count = daily_note_counter

                daily_note_last_contact = rec.env['res.partner.notes'].search([
                    ('partner_id', '=', rec.id), ('note_date', '<=', fields.Date.today())],
                    limit=1, order='note_date desc')

                if daily_note_last_contact and daily_note_last_contact.note_date:
                    rec.last_contact = daily_note_last_contact.note_date.date()

                daily_note_next_contact = rec.env['res.partner.notes'].search([
                    ('partner_id', '=', rec.id), ('note_date', '>', fields.Date.today())],
                    limit=1, order='note_date desc')
                if daily_note_next_contact and daily_note_next_contact.note_date:
                    rec.next_contact = daily_note_next_contact.note_date.date()

    def action_view_next_event(self):
        action = {
            'name': _(self.name + ' - Future Events'),
            'domain': [('partner_id', '=', self.ids), ('note_date', '>', fields.Date.today())],
            'view_type': 'form',
            'res_model': 'res.partner.notes',
            'view_id': self.env.ref('partner_daily_notes.partner_notes_view_tree').id,
            'view_mode': 'tree',
            'type': 'ir.actions.act_window',
        }
        if len(self) == 1:
            action['context'] = {'default_partner_id': self.id}
        return action
