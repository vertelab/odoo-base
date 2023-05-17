from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class User(models.Model):
    _inherit = 'res.users'

    def action_create_employee(self):
        res = super().action_create_employee()
        partner = self.partner_id
        if partner:
            partner.employee = True
        return res
    
    def update_all_employee_status(self):
        for user in self:
            employee = self.env['hr.employee'].search([('user_id', '=', user.id)])
            if employee:
                user.partner_id.employee = True
                
    def update_archived_employee_status(self):
        for user in self:
            employee = self.env['hr.employee'].search([('user_id', '=', user.id)])
            if employee:
                user.partner_id.employee = True

class HrEmployeePrivate(models.Model):
    _inherit = 'hr.employee'

    def toggle_active(self):
        res = super().toggle_active()
        for employee in self:
            if employee.active and employee.user_id:
                employee.user_id.partner_id.employee = True
            elif not employee.active and employee.user_id:
                employee.user_id.partner_id.employee = False
        return res