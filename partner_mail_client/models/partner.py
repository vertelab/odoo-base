from odoo import models, fields, api, _


class Partner(models.Model):
    _inherit = 'res.partner'

    mail_message_id = fields.One2many(
        'mail.message', 'author_id', string="Message", compute='_get_partners_message')
    show_messages = fields.Boolean(string="Show Messages", compute='_show_message')

    @api.depends('name')
    def _get_partners_message(self):
        for partner in self:
            partner.mail_message_id = [
                (6, 0, [m['id'] for m in self.env['mail.message'].search_read(
                    [
                        ('model', '=', 'res.partner'),
                        '|',
                        ('author_id', '=', partner.id),
                        ('partner_ids', '=', partner.id)
                    ],
                    ['id'])])]

    @api.depends('mail_message_id')
    def _show_message(self):
        for rec in self:
            if (len(rec.mail_message_id) > 0) and (self.id == self.env.user.partner_id.id):
                rec.show_messages = True
            else:
                rec.show_messages = False
