from odoo import models, fields, api, _

class ResPartner(models.Model):
    _inherit = "res.partner"
    
    show_for_support = fields.Boolean(compute="_compute_show_for_support", default=True)
    
    @api.multi
    def _compute_show_for_support(self):
        if not self.env.user.has_group('base_user_groups_dafa.1_line_support'):
            for partner in self:
                if partner.is_jobseeker or partner.user_id or partner.employee_id:
                    partner.show_for_support = False
    

