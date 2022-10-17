# Copyright 2020-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import xlrd
import base64
from datetime import datetime, timedelta

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HrContractMassive(models.Model):
    """Hr Contract Massive."""

    _name = "hr.contract.massive"
    _description = "Hr Contract Massive"

    @api.model
    def create(self, vals):
        """Create Sequence."""
        vals['name'] = self.env['ir.sequence'].next_by_code(
            'hr.contract.massive') or _('New')
        return super(HrContractMassive, self).create(vals)

    @api.depends('hr_contract_massive_lines_ids',
                 'hr_contract_massive_lines_ids.state')
    def _compute_is_all_done(self):
        for rec in self:
            if self.env['hr.contract.massive.lines'].search_count([
                    ('hr_contract_massive_id', '=', rec.id),
                    ('state', '=', 'draft')]) > 0:
                rec.is_all_done = False
            else:
                rec.is_all_done = True

    name = fields.Char(copy=False)
    date = fields.Date(default=fields.Date.context_today)
    file = fields.Binary()
    hr_contract_massive_lines_ids = fields.One2many(
        'hr.contract.massive.lines', 'hr_contract_massive_id')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('imported', 'Imported'),
        ('validate', 'Validate'),
        ('done', 'Done')], default='draft')
    is_all_done = fields.Boolean(compute='_compute_is_all_done', store=1)

    @api.multi
    def move_imported(self):
        for rec in self:
            if rec.file:
                workbook = xlrd.open_workbook(
                    file_contents=base64.decodestring(rec.file))
                row_lists = []
                row_list_flex = {}
                last_sheet = workbook.sheet_by_index(-1)
                # Will pick last sheet of the Excel Workbook
                for row in range(1, last_sheet.nrows):
                    row_lists.append(last_sheet.row_values(row))
                for row_list in row_lists:
                    if row_list[11]:
                        if row_list[0]:
                            last_employee = row_list[0]
                        if last_employee:
                            if not row_list_flex.get(last_employee):
                                row_list_flex.update(
                                    {last_employee: [
                                        [row_list[10], row_list[11]]]})
                            else:
                                row_list_flex.get(last_employee).append(
                                    [row_list[10], row_list[11]])
                for row_list in row_lists:
                    employee_id = wage = fix_wage_amount =\
                        date_start = date_end = job_id = department_id =\
                        struct_id = reason_change_id = False
                    if row_list[0]:
                        employee_id = self.env['hr.employee'].search(
                            [('name', '=', row_list[0])], limit=1)
                    if row_list[1]:
                        wage = row_list[1]
                    if row_list[2]:
                        fix_wage_amount = row_list[2]
                    if row_list[4]:
                        date_start = datetime(
                            *xlrd.xldate_as_tuple(row_list[4], 0)).date()
                    if row_list[5]:
                        date_end = datetime(
                            *xlrd.xldate_as_tuple(row_list[5], 0)).date()
                    if row_list[6]:
                        job_id = self.env['hr.job'].search(
                            [('name', '=', row_list[6])], limit=1)
                        if job_id:
                            job_id = job_id.id
                    if row_list[7]:
                        department_id = self.env['hr.department'].search(
                            [('name', '=', row_list[7])], limit=1)
                        if department_id:
                            department_id = department_id.id
                    if row_list[8]:
                        struct_id = self.env['hr.payroll.structure'].search(
                            [('name', '=', row_list[8])], limit=1)
                        if struct_id:
                            struct_id = struct_id.id
                    if row_list[9]:
                        reason_change_id = self.env[
                            'hr.contract.reason.change'].search(
                                [('name', '=', row_list[9])], limit=1)
                        if not reason_change_id:
                            reason_change_id = self.env[
                                'hr.contract.reason.change'].create(
                                    {'name': row_list[9]})
                        if reason_change_id:
                            reason_change_id = reason_change_id.id
                    contract = False
                    if employee_id and row_list[1]:
                        contract = self.env['hr.contract'].with_context(
                            from_novelty=True).create({
                                'name': employee_id.display_name + ' Contract',
                                'employee_id': employee_id.id,
                                'wage': wage,
                                'fix_wage_amount': fix_wage_amount,
                                'date_start': date_start,
                                'date_end': date_end,
                                'job_id': job_id,
                                'department_id': department_id,
                                'struct_id': struct_id,
                                'reason_change_id': reason_change_id,
                            })
                        if row_list_flex.get(row_list[0], '') and contract:
                            for flex_data in row_list_flex.get(
                                    row_list[0], ''):
                                self.env['hr.contract.flex_wage'].with_context(
                                    from_novelty=True).create({
                                        'contract_id': contract.id,
                                        'amount': flex_data[1],
                                        'salary_rule_id': self.env[
                                            'hr.salary.rule'].search(
                                                [('name', '=', flex_data[0])],
                                                limit=1).id or ''
                                    })
                        hr_contract_massive_lines_id = self.env[
                            'hr.contract.massive.lines'].create({
                                'employee_id': employee_id.id or False,
                                'wage': wage,
                                'fix_wage_amount': fix_wage_amount,
                                'date_start': date_start,
                                'date_end': date_end,
                                'hr_contract_massive_id': rec.id,
                                'job_id': job_id,
                                'department_id': department_id,
                                'struct_id': struct_id,
                                'reason_change_id': reason_change_id,
                            })
                        if contract:
                            hr_contract_massive_lines_id.write({
                                'hr_contract_id': contract.id,
                                'flex_wage_amount': contract.flex_wage_amount})
                            old_contract = self.env['hr.contract'].search([
                                ('id', '!=', contract.id),
                                ('employee_id', '=', contract.employee_id.id),
                                ('state', 'not in', ['close', 'cancel'])])
                            latest_contract = self.env['hr.contract'].search([
                                ('id', '!=', contract.id),
                                ('employee_id', '=', contract.employee_id.id),
                                ('state', 'not in', ['close', 'cancel'])],
                                order='create_date desc', limit=1)
                            if latest_contract.arl_percentage:
                                contract.write({
                                    'arl_percentage':
                                    latest_contract.arl_percentage})
                            if latest_contract and\
                                    latest_contract.date_start <=\
                                    contract.date_start - timedelta(days=1):
                                latest_contract.write({
                                    'date_end': contract.date_start -
                                    timedelta(days=1)})
                            if contract and\
                                    latest_contract:
                                contract.write({
                                    'subcontract': True,
                                    'father_contract_id': latest_contract.id})
                            if old_contract:
                                for old_con_rec in old_contract:
                                    old_con_rec.write({'state': 'close'})
                for row_list in row_lists:
                    employee_id = wage = fix_wage_amount =\
                        date_start = date_end = job_id = department_id =\
                        struct_id = reason_change_id = False
                    if row_list[0] and not row_list[1]:
                        employee_id = self.env['hr.employee'].search(
                            [('name', '=', row_list[0])], limit=1)
                        if employee_id:
                            old_contract = self.env['hr.contract'].search([
                                ('employee_id', '=', employee_id.id),
                                ('state', 'not in',
                                 ['close', 'cancel'])], limit=1)
                            if old_contract:
                                wage = old_contract.wage
                                date_start = old_contract.date_start
                                fix_wage_amount = old_contract.fix_wage_amount
                                date_end = old_contract.date_end
                                job_id = old_contract.job_id
                                department_id = old_contract.department_id
                                struct_id = old_contract.struct_id
                                reason_change_id =\
                                    old_contract.reason_change_id
                                hr_contract_massive_lines_id = self.env[
                                    'hr.contract.massive.lines'].create({
                                        'employee_id': employee_id.id or False,
                                        'wage': wage,
                                        'fix_wage_amount': fix_wage_amount,
                                        'date_start': date_start,
                                        'date_end': date_end,
                                        'hr_contract_massive_id': rec.id,
                                        'job_id': job_id.id,
                                        'department_id': department_id.id,
                                        'struct_id': struct_id.id,
                                        'reason_change_id':
                                        reason_change_id.id,
                                    })
                                hr_contract_massive_lines_id.write({
                                    'hr_contract_id': old_contract.id,
                                    'flex_wage_amount':
                                    old_contract.flex_wage_amount})
                if row_list_flex:
                    for line in rec.hr_contract_massive_lines_ids:
                        if line.hr_contract_id and\
                                line.hr_contract_id.flex_wage_ids and\
                                line.struct_id:
                            salary_rules =\
                                line.hr_contract_id.flex_wage_ids.mapped(
                                    'salary_rule_id.id')
                            if salary_rules:
                                for salary_rule in salary_rules:
                                    if salary_rule not in\
                                            line.struct_id.rule_ids.ids:
                                        line.struct_id.write(
                                            {'rule_ids': [(4,
                                                           salary_rule, None)
                                                          ]})
                rec.state = 'imported'

    @api.multi
    def move_validate(self):
        """Validate lines."""
        for rec in self:
            for line in rec.hr_contract_massive_lines_ids:
                message = ''
                if not line.employee_id:
                    message += " Employee isn't created."
                if not line.hr_contract_id:
                    message += " Contract isn't created."
                if not line.struct_id:
                    message += " Salary Structure isn't created."
                if message == '':
                    line.hr_contract_id.write({
                        'state': 'open'})
                    line.state = 'done'
                line.comment = message
            rec.state = 'validate'

    @api.multi
    def move_done(self):
        """Move to Done."""
        for rec in self:
            if self.env['hr.contract.massive.lines'].search_count([
                    ('hr_contract_massive_id', '=', rec.id),
                    ('state', '=', 'draft')]) > 0:
                raise ValidationError(_(
                    'All Contract Line should be Done.'))
            rec.state = 'done'

    @api.multi
    def move_draft(self):
        for rec in self:
            rec.write({'hr_contract_massive_lines_ids': [(5, 0, 0)],
                       'file': False,
                       'state': 'draft'})

    @api.multi
    def create_subcontract(self):
        """Create Subcontract."""
        for rec in self:
            for line in rec.hr_contract_massive_lines_ids:
                line.create_subcontract()


class HrContractMassiveLines(models.Model):
    """Hr Contract Massive Lines."""

    _name = "hr.contract.massive.lines"
    _description = "Hr Contract Massive Lines"

    hr_contract_massive_id = fields.Many2one('hr.contract.massive')
    employee_id = fields.Many2one('hr.employee')
    wage = fields.Float()
    fix_wage_amount = fields.Float()
    flex_wage_amount = fields.Float()
    date_start = fields.Date()
    date_end = fields.Date()
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done')], default='draft')
    comment = fields.Text()
    hr_contract_id = fields.Many2one('hr.contract')
    job_id = fields.Many2one('hr.job')
    department_id = fields.Many2one('hr.department')
    struct_id = fields.Many2one('hr.payroll.structure')
    reason_change_id = fields.Many2one('hr.contract.reason.change')

    @api.multi
    def create_subcontract(self):
        """Create Subcontract."""
        for rec in self:
            contract_id = rec.hr_contract_id
            if contract_id.subcontract:
                contract_id.write({
                    'subcontract': False, 'father_contract_id': ''})
            new_subcontract_id = contract_id.with_context(
                from_novelty=True).copy()
            new_subcontract_id.write({
                'subcontract': True, 'father_contract_id': contract_id.id,
                'date_start': contract_id.date_start,
                'date_end': contract_id.date_end,
                'state': 'open'})
            if new_subcontract_id.date_start:
                contract_id.write({'date_end': new_subcontract_id.date_start})
            contract_id.write({
                'state': 'close', 'subcontract': False})
            if new_subcontract_id:
                rec.hr_contract_id = new_subcontract_id.id
                rec.state = 'done'
