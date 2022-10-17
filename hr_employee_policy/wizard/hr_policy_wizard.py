# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class HRPolicyWizard(models.TransientModel):
    _name = 'hr.policy.wizard'
    _description = 'HR Policy Wizard'

    policy_ids = fields.Many2many(
        'hr.policy', string='Policy',
        domain=lambda self: self._get_employee_policy())

    @api.model
    def _get_employee_policy(self):
        """
        This methods used for get remaining the policy
        of employee in the wizard
        :return:
        """
        hr_employee_policy_ids = self.env['hr.employee.policy'].search(
            [('employee_id', '=', self._context.get('active_id', False))])
        hr_policy_ids = hr_employee_policy_ids.mapped('hr_policy_id')
        res = [('id', 'not in', hr_policy_ids.ids)]
        return res

    @api.multi
    def generate_employee_policy(self):
        """
        This methods generate the employee policy for the selected
        policy in the wizard
        :return:
        """
        HREmpPolicy = self.env['hr.employee.policy']
        employee_id = self._context.get('active_id', False)
        for policy_id in self.policy_ids:
            HREmpPolicy.create({
                'description': policy_id.description,
                'check_read': policy_id.check_read,
                'date': policy_id.date,
                'answer_type': policy_id.answer_type,
                'template_id': policy_id.template_id.id,
                'hr_policy_id': policy_id.id,
                'employee_id': employee_id
            })
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
