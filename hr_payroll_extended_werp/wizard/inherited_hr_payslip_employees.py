# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import threading
import logging
_logger = logging.getLogger(__name__)


class HrPayslipEmployees(models.TransientModel):
    """Hr Payslip Employees."""

    _inherit = "hr.payslip.employees"

    @api.multi
    def compute_sheet_1(self):
        message = 'The process finish in (%s) seconds!' % (
            3 * len(self.employee_ids))
        view_id = self.env.ref(
            'hr_payroll_extended_werp.hr_payslip_employees_confirm_wizard').id
        thread = threading.Thread(target=self.with_context(
            progress_action=threading.get_ident()).compute_sheet_thread, args=(
        ))
        thread.start()
        active_id = self.env.context.get('active_id')
        hr_payslip_run_id = self.env['hr.payslip.run'].browse(active_id)
        # hr_payslip_run_id.message_post(
        #     subject="Compute Sheet Process.",
        #     body=_(
        #         "The Compute Sheet process is generating in this moment "
        #         "please wait Process:- %s Date:- %s" % (
        #             threading.get_ident(), fields.Date.today())))
        res = {
            'name': _('Confirm'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.payslip.employees.confirm.wizard',
            'view_id': view_id,
            'target': 'new',
            'context': {'message': message},
        }
        return res

    @api.multi
    def compute_sheet_thread(self):
        try:
            with api.Environment.manage():
                new_cr = self.pool.cursor()
                self = self.with_env(self.env(cr=new_cr))
                self.compute_sheet()
                new_cr.commit()
                new_cr.close()
            return {'type': 'ir.actions.act_window_close'}
        except Exception as error:
            _logger.info(error)
            active_id = self.env.context.get('active_id')
            payslip_run_id = self.env['hr.payslip.run'].browse(active_id)
            payslip_run_id.result_process = error

    @api.multi
    def compute_sheet(self):
        """Overwrite compute sheet for check contract date."""
        payslips = self.env['hr.payslip']
        [data] = self.read()
        date_from = ''
        active_id = self.env.context.get('active_id')
        if active_id:
            [run_data] = self.env['hr.payslip.run'].browse(
                active_id).read(['date_start', 'date_end', 'credit_note',
                                 'pay_annual', 'pay_biannual', 'rule_ids',
                                 'pay_contributions'])
        from_date = run_data.get('date_start')
        to_date = run_data.get('date_end')
        if not data['employee_ids']:
            raise UserError(
                _("You must select employee(s) to generate payslip(s)."))
        for employee in self.env['hr.employee'].browse(data['employee_ids']):
            to_date = run_data.get('date_end')
            from_date = run_data.get('date_start')
            slip_data = self.env['hr.payslip'].onchange_employee_id(
                from_date, to_date, employee.id, contract_id=False)
            contract = self.env['hr.contract'].browse(slip_data['value'].get(
                'contract_id'))
            if contract.date_start and\
                    contract.date_start.month == from_date.month and\
                    contract.date_start.year == from_date.year:
                from_date = contract.date_start
            if contract.date_end and\
                    contract.date_end.month == to_date.month and\
                    contract.date_end.year == to_date.year:
                to_date = contract.date_end
            res = {
                'employee_id': employee.id,
                'name': slip_data['value'].get('name'),
                'struct_id': slip_data['value'].get('struct_id'),
                'contract_id': slip_data['value'].get('contract_id'),
                'payslip_run_id': active_id,
                'input_line_ids': [(0, 0, x) for x in slip_data['value'].get(
                    'input_line_ids')],
                'worked_days_line_ids': [(0, 0, x) for x in slip_data[
                    'value'].get('worked_days_line_ids')],
                'date_from': str(from_date),
                'date_to': str(to_date),
                'credit_note': run_data.get('credit_note'),
                'pay_annual': run_data.get('pay_annual'),
                'pay_biannual': run_data.get('pay_biannual'),
                'pay_contributions': run_data.get('pay_contributions'),
                'rule_ids': [(6, 0, run_data.get('rule_ids'))],
                'company_id': employee.company_id.id,
            }
            worked_days_line_ids = {}
            worked_days_line_ids = self.env['hr.payslip'].get_worked_day_lines(
                contract, date_from or from_date, to_date)
            if res.get('worked_days_line_ids', ''):
                res.update(
                    {'worked_days_line_ids': [
                        (0, 0, x) for x in worked_days_line_ids]})
            date_from = ''
            payslips = self.env['hr.payslip'].create(res)
            payslips.compute_sheet()
        # payslip_run_id = self.env['hr.payslip.run'].browse(active_id)
        # payslip_run_id.result_process = "The process finish correctly"
        return {'type': 'ir.actions.act_window_close'}


class UpdateLeavesDetails(models.TransientModel):

    _name = "update.leaves.details.wizard"
    _description = "Update Leaves Details"

    employee_ids = fields.Many2many(
        'hr.employee', string='Employees', copy=False)

    @api.model
    def default_get(self, fields):
        res = super(UpdateLeavesDetails, self).default_get(fields)
        active_ids = self._context.get('active_ids')
        employees = self.env['hr.employee'].browse(active_ids)
        res.update({'employee_ids': [(6, 0, employees.ids)]})
        return res

    @api.multi
    def update_leaves_details(self):
        for employee_id in self.employee_ids:
            employee_id.calculate_leaves_details()


class HrPayslipEmployeesConfirmWizard(models.TransientModel):
    _name = 'hr.payslip.employees.confirm.wizard'
    _description = 'Hr Payslip Employees Confirm Wizard'

    @api.multi
    def get_message(self):
        if self.env.context.get("message", False):
            return self.env.context.get("message")
        return False

    message = fields.Text(
        string="Message",
        readonly=True,
        default=get_message)


class MultiActionAccumulate(models.TransientModel):
    _name = 'multi.action.accumulate'
    _description = 'Multi Action Accumulate'

    @api.model
    def default_get(self, fields):
        res = super(MultiActionAccumulate, self).default_get(fields)
        active_ids = self._context.get('active_ids')
        hr_payslip_ids = self.env['hr.payslip'].browse(active_ids)
        res.update({'hr_payslip_ids': [(6, 0, hr_payslip_ids.ids)]})
        return res

    @api.multi
    def action_acumulate(self):
        for hr_payslip_id in self.hr_payslip_ids:
            if hr_payslip_id.state == 'done':
                hr_payslip_id.action_acumulate()

    hr_payslip_ids = fields.Many2many('hr.payslip', string='Payslips')
