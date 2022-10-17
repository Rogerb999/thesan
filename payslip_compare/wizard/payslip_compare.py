# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PayslipCompare(models.TransientModel):
    """"Payslip Compare."""

    _name = 'payslip.compare'

    MONTH_SELECTION = [
        ('01', 'January'), ('02', 'February'),
        ('03', 'March'), ('04', 'April'),
        ('05', 'May'), ('06', 'June'),
        ('07', 'July'), ('08', 'August'),
        ('09', 'September'), ('10', 'October'),
        ('11', 'November'), ('12', 'December'),
    ]

    employee_ids = fields.Many2many(
        'hr.employee', string='Employee', required=True)
    first_month = fields.Selection(
        MONTH_SELECTION, string=' First Month', required=True)
    second_month = fields.Selection(
        MONTH_SELECTION, string='Second Month', required=True)

    @api.multi
    def compare_payslip_total(self):
        """For the selected months payslip date calculation."""
        first_month_date = self.first_month + '/' + \
            '01' + '/' + str(datetime.today().year)
        second_month_date = self.second_month + '/' + \
            '01' + '/' + str(datetime.today().year)
        # Previous records deletion to display the latest result
        self._cr.execute("DELETE FROM payslip_compare_result;")
        if not self.employee_ids:
            raise UserError(_("Please select the employee"))
        for employee in self.employee_ids:
            employee_diff = {}
            first_month_salary_slip = self.env['hr.payslip'].search(
                [('employee_id', '=', employee.id),
                 ('date_from', '=', first_month_date)])
            second_month_salary_slip = self.env['hr.payslip'].search(
                [('employee_id', '=', employee.id),
                 ('date_from', '=', second_month_date)])
            payslip_name_list = [payslip_id.name for payslip_id in first_month_salary_slip]
            if first_month_salary_slip and second_month_salary_slip:
                # Considering last Payslip in case multiple salary slip of same
                # month and same year is found
                first_slip = first_month_salary_slip[
                    len(first_month_salary_slip) - 1]
                second_slip = second_month_salary_slip[
                    len(second_month_salary_slip) - 1]
                if first_slip.details_by_salary_rule_category and\
                        second_slip.details_by_salary_rule_category:
                    # Salary rule wise difference in Payslip of both the
                    # selected months
                    total_diff = list(map(
                        lambda total1, total2: dict(
                            {total1.name: abs(total1.total - total2.total)}),
                        first_slip.details_by_salary_rule_category,
                        second_slip.details_by_salary_rule_category))

                    employee_diff[employee] = total_diff
                    # Record creation to display the result.
                    if total_diff:
                        for vals in total_diff:
                            self.env['payslip.compare.result'].create({
                                'payslip_name': ",".join(payslip_name_list),
                                'employee_id': employee.id,
                                'rule_name': list(vals.keys())[0],
                                'difference': vals[list(vals.keys())[0]],
                            })
                else:
                    raise UserError(_(
                        "Salary rule lines are not available "
                        "in salary slip of employee %s")
                        % (employee.name,))
            else:
                raise UserError(
                    _("Salary slip is not available of employee %s") % (
                        employee.name,))
        self.ensure_one()
        tree_view_id = self.env.ref(
            'payslip_compare.payslip_compare_result_view_tree').id
        # Returns the tree view of created records
        if tree_view_id:
            return {
                'name': _('Payslip Comparision Result'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'payslip.compare.result',
                'views': [(tree_view_id, 'tree')],
                'context': {'search_default_employee_payslip_diff': 1}
            }
