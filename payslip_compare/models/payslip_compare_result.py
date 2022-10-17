# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class PayslipCompareResult(models.Model):
    """Payslip Compare Result."""

    _name = 'payslip.compare.result'

    employee_id = fields.Many2one('hr.employee', string="Employee")
    difference = fields.Float(string="Difference")
    rule_name = fields.Char(string="Salary Rule ")
    payslip_name = fields.Char('Payslip')
