# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _


class HRPolicy(models.Model):
    _name = 'hr.policy'
    _description = 'HR Policy'

    name = fields.Char('Name', required=True)
    description = fields.Text('Description')
    check_read = fields.Boolean('Read')
    date = fields.Date('Date')
    answer_type = fields.Selection([('yes', 'Yes'), ('no', 'No')])
    template_id = fields.Many2one(
        'mail.template', 'Template',
        domain=[('model_id.model', '=', 'hr.policy')])
    policy_for_employee = fields.Boolean('Create default policy for employee?')

    @api.multi
    def view_employees_policy(self):
        hr_employee_policy_ids = self.env['hr.employee.policy'].search([
            ('hr_policy_id', '=', self.id)])
        return {
            'name': _('HR Employee Policy'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'hr.employee.policy',
            'domain': [('id', '=', hr_employee_policy_ids.ids)],
            'type': 'ir.actions.act_window',
        }
