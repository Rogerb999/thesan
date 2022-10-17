# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class HrEmployeeAcumulate(models.Model):
    """Hr Employee Acumulate."""

    _name = "hr.employee.acumulate"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Hr Employee Acumulate"

    name = fields.Char()
    employee_id = fields.Many2one('hr.employee', 'Employee')
    hr_rules_acumulate_id = fields.Many2one(
        'hr.conf.acumulated', 'Acumulate Rules')
    total_acumulate = fields.Float()
    pay_slip_id = fields.Many2one('hr.payslip', 'Payslip')
    description = fields.Text()

    @api.onchange('pay_slip_id')
    def onchange_pay_slip_id(self):
        """Calculate total acumulate."""
        for rec in self:
            if rec.pay_slip_id.line_ids and rec.total_acumulate == 0.0:
                total_acumulate = 0.0
                for payslip_line in rec.pay_slip_id.line_ids:
                    if rec.hr_rules_acumulate_id.rules_add_ids:
                        for rule_add in\
                                rec.hr_rules_acumulate_id.rules_add_ids:
                            if rule_add.rule_id ==\
                                    payslip_line.salary_rule_id:
                                total = payslip_line.total
                                if payslip_line.total < 0:
                                    total = -total
                                total_acumulate += total
                for payslip_line in rec.pay_slip_id.line_ids:
                    if rec.hr_rules_acumulate_id.rules_substract_ids:
                        for rule_substract in\
                                rec.hr_rules_acumulate_id.rules_substract_ids:
                            if rule_substract.rule_id ==\
                                    payslip_line.salary_rule_id:
                                total = payslip_line.total
                                if payslip_line.total < 0:
                                    total = -total
                                total_acumulate -= total
                if total_acumulate == 0:
                    rec.unlink()
                else:
                    rec.total_acumulate = total_acumulate
