import logging

from odoo.tools.translate import _
from odoo.tools import email_split
from odoo.exceptions import UserError

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class PortalWizardUser(models.TransientModel):
    """
        A model to configure users in the portal wizard.
    """

    _inherit = 'portal.wizard.user'

    def action_apply(self):
        self.env['res.partner'].check_access_rights('write')
        """ From selected partners, add corresponding users to chosen portal group. It either granted
            existing user, or create new one (and add it to the group).
        """
        error_msg = self.get_error_messages()
        if error_msg:
            raise UserError("\n\n".join(error_msg))

        default_portal_role_id = self.env['ir.config_parameter'].sudo().get_param('portal_role_id')

        for wizard_user in self.sudo().with_context(active_test=False):

            group_portal = self.env.ref('base.group_portal')
            # Checking if the partner has a linked user
            user = wizard_user.partner_id.user_ids[0] if wizard_user.partner_id.user_ids else None
            # update partner email, if a new one was introduced
            if wizard_user.partner_id.email != wizard_user.email:
                wizard_user.partner_id.write({'email': wizard_user.email})
            # add portal group to relative user of selected partners
            if wizard_user.in_portal:
                user_portal = None
                # create a user if necessary, and make sure it is in the portal group
                if not user:
                    if wizard_user.partner_id.company_id:
                        company_id = wizard_user.partner_id.company_id.id
                    else:
                        company_id = self.env.company.id
                    user_portal = wizard_user.sudo().with_company(company_id)._create_user()
                else:
                    user_portal = user
                wizard_user.write({'user_id': user_portal.id})
                if not wizard_user.user_id.active or group_portal not in wizard_user.user_id.groups_id:
                    wizard_user.user_id.write({'active': True, 'groups_id': [(4, group_portal.id)]})
                    # prepare for the signup process
                    wizard_user.user_id.partner_id.signup_prepare()
                wizard_user.with_context(active_test=True)._send_email()

                self._assign_user_role(default_portal_role_id, user_portal)

                wizard_user.refresh()
            else:
                # remove the user (if it exists) from the portal group
                if user and group_portal in user.groups_id:
                    # if user belongs to portal only, deactivate it
                    if len(user.groups_id) <= 1:
                        user.write({'groups_id': [(3, group_portal.id)], 'active': False})
                    else:
                        user.write({'groups_id': [(3, group_portal.id)]})

                    self._assign_user_role(default_portal_role_id, user)

    def _assign_user_role(self, default_portal_role_id, user):
        if default_portal_role_id:
            default_portal_role_id = self.env['res.users.role'].browse(int(default_portal_role_id)).exists()
            user_in_role = default_portal_role_id.line_ids.filtered(lambda x: x.user_id.id == 9)

            if not user_in_role:
                default_portal_role_id.write({
                    'line_ids': [(0, 0, {
                        'user_id': user.id,
                        'is_enabled': True
                    })]
                })
            else:
                default_portal_role_id.write({'line_ids': [(2, user_in_role.id)]})



