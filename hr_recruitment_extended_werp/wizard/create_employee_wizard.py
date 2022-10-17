# -*- coding: utf-8 -*-

from odoo import api, fields, models


class CreateEmployeeWizard(models.TransientModel):
    _name = 'hr.create.employee.wizard'
    _description = 'HR Create Employee'

    work_email = fields.Text(string="Work Mail")
    department_id = fields.Many2one(
        'hr.department', string='Department')
    job_id = fields.Many2one(
        'hr.job', string='Job')
    macro_area_id = fields.Many2one(
        'macro.area', string='Macro Area')
    work_group_id = fields.Many2one(
        'work.group', string='Work Group')
    function_execute_id = fields.Many2one(
        'function.executed', string='Fuction Excecuted')
    parent_id = fields.Many2one(
        'hr.employee', string='Responsable')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
        ])
    birthday = fields.Date(string='Birthday')
    bank_account_id = fields.Many2one(
        'res.partner.bank', string='Bank Account')

    @api.multi
    def confirm(self):
        active_id = self.env.context.get('active_id')
        partner_id = self.env['res.partner'].browse(active_id)
        employee_id = self.env['hr.employee'].create({
            'name': partner_id.name,
            'work_email': self.work_email,
            'department_id': self.department_id.id,
            'job_id': self.job_id.id,
            'macro_area_id': self.macro_area_id.id,
            'work_group_id': self.work_group_id.id,
            'function_executed_id': self.function_execute_id.id,
            'job_title': self.job_id.name,
            'parent_id': self.parent_id.id,
            'address_home_id': partner_id.id,
            'gender': self.gender,
            'birthday': self.birthday,
            'bank_account_id': self.bank_account_id.id,
            })
