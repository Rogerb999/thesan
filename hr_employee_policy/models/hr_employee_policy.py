# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class HREmployeePolicy(models.Model):
    _name = 'hr.employee.policy'
    _description = 'HR Employee Policy'

    name = fields.Char('Name', compute='_get_name', store=True)
    description = fields.Text('Description')
    check_read = fields.Boolean('Read')
    date = fields.Date('Date')
    answer_type = fields.Selection([('yes', 'Yes'), ('no', 'No')])
    hr_policy_id = fields.Many2one('hr.policy', 'Policy', required=True)
    employee_id = fields.Many2one(
        'hr.employee', 'Employee', required=True,
        )
    template_id = fields.Many2one(
        'mail.template', 'Template',
        domain=[('model_id.model', '=', 'hr.policy')])
    additional_note = fields.Text()

    @api.model
    def create(self, vals):
        if vals.get('employee_id', ''):
            return super(HREmployeePolicy, self).create(vals)

    @api.one
    @api.depends('hr_policy_id', 'employee_id')
    def _get_name(self):
        name = 'New'
        if self.employee_id and self.hr_policy_id:
            name = "%s - %s" % (self.employee_id.name, self.hr_policy_id.name)
        elif self.employee_id:
            name = self.employee_id.name
        elif self.hr_policy_id:
            name = self.hr_policy_id.name
        self.name = name
