# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class HREmployeePolicyWizard(models.TransientModel):
    _name = 'hr.employee.policy.wizard'
    _description = 'HR Employee Policy Wizard'

    employee_ids = fields.Many2many(
        'hr.employee', string='Employees',
        domain=lambda self: self._get_employees())

    @api.model
    def _get_employees(self):
        """
        This methods used for get remaining the employee for the selected
        employees in the wizard
        :return:
        """
        hr_employee_policy_ids = self.env['hr.employee.policy'].search(
            [('hr_policy_id', '=', self._context.get('active_id', False))])
        res = [('id', 'not in', [
            res.employee_id.id for res in hr_employee_policy_ids])]
        return res

    @api.multi
    def generate_hr_policy(self):
        """
        This methods generate the employee policy for the selected
        employees in the wizard
        :return:
        """
        HREmpPolicy = self.env['hr.employee.policy']
        hr_policy_id = self.env['hr.policy'].browse(
            self._context.get('active_id', False))
        for employee_id in self.employee_ids:
            HREmpPolicy.create({
                'employee_id': employee_id.id,
                'hr_policy_id': hr_policy_id.id,
                'description': hr_policy_id.description,
                'date': hr_policy_id.date,
                'answer_type': hr_policy_id.answer_type,
                'check_read': hr_policy_id.check_read,
                'template_id': hr_policy_id.template_id.id,
            })
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
