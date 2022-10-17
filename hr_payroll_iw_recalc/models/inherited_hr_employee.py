# Copyright 2020-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import fields, models


class HrEmployee(models.Model):
    """Hr Employee."""

    _inherit = "hr.employee"

    def _compute_hr_recalc_lines(self):
        for rec in self:
            rec.hr_recalc_lines_count = self.env[
                'hr.recalc.lines'].search_count([('employee_id', '=', rec.id)])

    hr_recalc_lines_count = fields.Integer(compute='_compute_hr_recalc_lines',
                                           string='Hr Recalc Lines Count')

    def create_iw(self, date, payslip_id):
        """Create IW."""
        res = 0
        hr_recalc_lines = self.env['hr.recalc.lines'].search([(
            'payslip_id', '=', payslip_id.id)])
        payslip = self.env['hr.payslip'].search([(
            'id', '=', payslip_id.id)])
        if hr_recalc_lines:
            print("hr_recalc_lines", hr_recalc_lines)
            payslip.write({'recalc_line_id': hr_recalc_lines.id})
        if payslip_id.recalc_line_id:
            return res
        elif date and payslip_id:
            date_end = date
            date_start = date - relativedelta(months=12)
            date_start = date_start.replace(day=1)
            hr_payslip_iw_recalc = self.env['hr.payslip.iw.recalc'].create({
                'name': self.name,
                'date_start': date_start,
                'date_end': date_end
            })
            hr_recalc_lines = self.env['hr.recalc.lines'].create({
                'hr_payslip_iw_recalc_id': hr_payslip_iw_recalc.id,
                'employee_id': self.id,
                'payslip_id': payslip_id.id
            })
            hr_recalc_lines.compute_sheet_rf()
            payslip.write({'recalc_line_id': hr_recalc_lines.id})
            if hr_recalc_lines:
                result = hr_recalc_lines.total_retention_income
        return res
