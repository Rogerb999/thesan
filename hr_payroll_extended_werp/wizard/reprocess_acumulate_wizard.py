# Copyright 2020-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ReprocessAcumulateWizard(models.TransientModel):
    _name = 'reprocess.acumulate.wizard'
    _description = 'reprocess.acumulate.wizard'

    sequence = fields.Integer()
    option = fields.Selection([
        ('better', 'Better'),
        ('rules', 'Rules')], default='better')
    hr_salary_rule_ids = fields.Many2many(
        'hr.salary.rule', 'reprocess_acumulate_wizard_hr_salary_rule_rel',
        'reprocess_acumulate_wizard_id', 'hr_salary_rule_id')

    @api.multi
    def confirm(self):
        if self.env.context.get('active_model') == 'hr.payslip.run':
            hr_payslip_ids = self.env[self.env.context.get(
                'active_model')].browse(
                    self.env.context.get('active_id')).slip_ids
        if self.env.context.get('active_model') == 'hr.payslip':
            hr_payslip_ids = self.env[self.env.context.get(
                'active_model')].browse(self.env.context.get('active_ids'))
        aux = 0
        for hr_payslip_id in hr_payslip_ids:
            aux += 1
            contract_ids = hr_payslip_id.contract_id.ids or \
                hr_payslip_id.get_contract(
                    hr_payslip_id.employee_id, hr_payslip_id.date_from,
                    hr_payslip_id.date_to)
            if hr_payslip_id.state == 'done' and contract_ids:
                if self.option == 'better':
                    if self.sequence < 500:
                        raise ValidationError(_(
                            'Sequence value can not be less than 500.'))
                    for line in hr_payslip_id.line_ids:
                        if line.salary_rule_id.sequence > self.sequence:
                            line.unlink()
                    for line in hr_payslip_id._get_payslip_lines(
                            contract_ids, hr_payslip_id.id):
                        salary_rule_id = self.env['hr.salary.rule'].browse(
                            line.get('salary_rule_id', ''))
                        if salary_rule_id.sequence > self.sequence:
                            line.update({'slip_id': hr_payslip_id.id})
                            self.env['hr.payslip.line'].create(line)
                    hr_payslip_id.action_acumulate()
                if self.option == 'rules' and self.hr_salary_rule_ids:
                    for line in hr_payslip_id.line_ids:
                        if line.salary_rule_id.id in\
                                self.hr_salary_rule_ids.ids:
                            line.unlink()
                    for line in hr_payslip_id._get_payslip_lines(
                            contract_ids, hr_payslip_id.id):
                        salary_rule_id = self.env['hr.salary.rule'].browse(
                            line.get('salary_rule_id', ''))
                        if salary_rule_id.id in self.hr_salary_rule_ids.ids:
                            line.update({'slip_id': hr_payslip_id.id})
                            self.env['hr.payslip.line'].create(line)
                    hr_payslip_id.action_acumulate()
