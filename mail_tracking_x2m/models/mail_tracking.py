from odoo import models

class MailTracking(models.Model):
    _inherit = 'mail.tracking.value'

    def create_tracking_values(self, initial_value, new_value, col_name, col_info, track_sequence):
        """ Implement tracking for Many2many and One2many.
            Why the frack is this not in core? Is there som horrible consequence lurking in the deep?
        """
        # TODO: Look at the presentation end of this. Look at how Many2one is implemented.
        if col_info['type'] in ('many2many', 'one2many'):
            return {
                'field': col_name,
                'field_desc': col_info['string'],
                'field_type': col_info['type'],
                'track_sequence': track_sequence,
                'old_value_char': initial_value and ', '.join(initial_value.sudo().mapped('display_name')) or '',
                'new_value_char': new_value and ', '.join(new_value.sudo().mapped('display_name')) or ''}
        return super(MailTracking, self).create_tracking_values(
            initial_value, new_value, col_name, col_info, track_sequence)
