# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    contact_reference_ids = fields.One2many(
        'contact.reference', 'employee_id',
        string='Contact Reference')
    policy_ids = fields.One2many(
        'hr.employee.policy', 'employee_id',
        string='Policies')

    @api.model
    def create(self, vals):
        res = super(HrEmployee, self).create(vals)
        policy_ids = self.env['hr.policy'].search(
            [('policy_for_employee', '=', True)])
        hr_policy_employee = self.env['hr.employee.policy']
        for policy_id in policy_ids:
            hr_policy_employee.create({
                'description': policy_id.description,
                'check_read': policy_id.check_read,
                'date': policy_id.date,
                'answer_type': policy_id.answer_type,
                'template_id': policy_id.template_id.id,
                'hr_policy_id': policy_id.id,
                'employee_id': res.id
            })
        return res

    @api.multi
    def view_policy_records(self):
        hr_policy_employee = self.env['hr.employee.policy'].search(
            [('employee_id', '=', self.id)])
        return {
            'name': _('Employee Policy'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'hr.employee.policy',
            'domain': [('id', '=', hr_policy_employee.ids)],
            'type': 'ir.actions.act_window',
        }
