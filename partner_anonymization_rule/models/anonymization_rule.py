import logging
from odoo import _, api, fields, models
from odoo.exceptions import AccessError, UserError

_logger = logging.getLogger(__name__)

class AnonymizeRule(models.Model):
    _name = 'anonymization.rule'
    _description = "Anonymization Rules"

    name = fields.Char()
    model_id = fields.Many2one('ir.model', string='Model to Anonymize', domain=[('transient', '=', False)])
    model_name = fields.Char(related='model_id.model', string='Model Name', readonly=True, store=True)
    domain = fields.Char(default="[]", help="Domain applied to the active id of the parent model")

    def action_anonymize(self):
        if not self.env.user.has_group(
                "privacy_partner_to_be_forgotten.group_partner_anonymize"
        ):
            raise AccessError(_("You don't have permission to anonymize partners."))

        self.process_anonymization_rule()


    def process_anonymization_rule(self):
        rec_ids = self.env[self.model_id.model].search(eval(self.domain))
        if self.model_id.model == 'res.partner':
            partner_ids = rec_ids
        else:
            partner_ids = rec_ids.mapped('partner_id')

        for partner in partner_ids:
            partner.anonymize_partner_data()


    def _process_anonymization_rule(self):
        anonymization_rule_ids = self.env['anonymization.rule'].search([])
        for anonymization_rule in anonymization_rule_ids:
            try:
                anonymization_rule.process_anonymization_rule()
            except Exception as e:
                _logger.error(f"{e}")