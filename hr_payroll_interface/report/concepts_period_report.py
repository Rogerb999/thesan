# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models
from datetime import datetime


class ConceptsPeriodReport(models.AbstractModel):
    """Calculation for the report."""

    _name = 'report.hr_payroll_interface.concepts_period_template'
    _description = "HR Payroll Concept Period Template"

    def get_detail(self, rec):
        """Get the details of payslip line."""
        res_data = []
        res = rec.payslip_ids.mapped('line_ids.name')
        if res:
            res = list(set(res))
            hr_payslip_line_obj = self.env['hr.payslip.line']
            for line in res:
                quantity = 0
                accruals = 0
                deductions = 0
                for slip_lines in hr_payslip_line_obj.search(
                        [('slip_id', 'in', rec.payslip_ids.ids),
                         ('name', '=', line)]):
                    if slip_lines.total < 0:
                        quantity += slip_lines.quantity
                        deductions += -slip_lines.total
                    elif slip_lines.total >= 0:
                        quantity += slip_lines.quantity
                        accruals += slip_lines.total
                res_data.append({
                    'name': slip_lines.salary_rule_id.code_sara,
                    'quantity': quantity,
                    'accruals': accruals,
                    'deductions': deductions
                })
        return res_data

    def get_first_date(self, rec):
        """Get first td date."""
        return 'M' + rec.strftime('%Y') + rec.strftime('%m') + '-NOMINA ' +\
            rec.strftime('%B') + ' ' + rec.strftime('%Y')

    def get_second_date(self, rec):
        """Get second td date."""
        return '1-NOMINA ' + rec.strftime('%B') + ' ' + rec.strftime('%Y')

    @api.model
    def _get_report_values(self, docids, data=None):
        lang_code = self.env.context.get('lang') or 'en_US'
        lang = self.env['res.lang']
        lang_id = lang._lang_get(lang_code)
        strftime_format = (u"%s %s" %
                           (lang_id.date_format, lang_id.time_format))
        pi = self.env['hr.payroll.interface'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'hr.payroll.interface',
            'data': data,
            'docs': pi,
            'get_detail': self.get_detail,
            'get_first_date': self.get_first_date,
            'get_second_date': self.get_second_date,
            'current_datetime': datetime.now().strftime(strftime_format),
        }
