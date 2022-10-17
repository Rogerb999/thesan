# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from dateutil.relativedelta import relativedelta
import pytz
from pytz import timezone
from datetime import datetime, time
import calendar
from odoo import api, models, fields, _
from odoo.exceptions import ValidationError


class HrPayslip(models.Model):
    """Overwrite the hr payslip."""

    _inherit = "hr.payslip"

    eps_id = fields.Many2one(
        'res.partner', 'EPS', domain="[('is_eps', '=', True)]")
    pension_fund_id = fields.Many2one(
        'res.partner', 'Pension Fund')
    unemployment_fund_id = fields.Many2one(
        'res.partner', 'Unemployment Fund',
        domain="[('is_unemployee_fund', '=', True)]")
    arl_id = fields.Many2one(
        'res.partner', 'ARL')
    prepaid_medicine_id = fields.Many2one(
        'res.partner', 'Prepaid Medicine')
    prepaid_medicine2_id = fields.Many2one(
        'res.partner', 'Prepaid Medicine 2')
    afc_id = fields.Many2one(
        'res.partner', 'AFC',
        domain="[('is_afc', '=', True)]")
    voluntary_contribution_id = fields.Many2one(
        'res.partner', 'Voluntary Contribution',
        domain="[('is_voluntary_contribution', '=', True)]")
    bank_account_id = fields.Many2one(
        'res.partner.bank', 'Bank Account Number',
        help='Employee bank salary account')
    unjustified = fields.Boolean(
        readonly=True,
        states={'draft': [('readonly', False)]})
    transfer_employee = fields.Boolean(
        readonly=True,
        copy=False,
        states={'draft': [('readonly', False)]})
    contract_completion = fields.Boolean('Contract Completion?')
    compensation_company_id = fields.Many2one(
        'res.company', 'Compensation Company',
        default=lambda self: self.env.user.company_id)
    voluntary_contribution2_id = fields.Many2one(
        'res.partner', 'Voluntary Contribution2',
        domain="[('is_voluntary_contribution', '=', True)]")

    @api.multi
    def unlink(self):
        res = True
        for s_id in self:
            s_id.ps_input_rf_ids.unlink()
            s_id.ps_input_no_rf_ids.unlink()
            s_id.ps_deductions_ids.unlink()
            s_id.ps_renting_additional_ids.unlink()
            s_id.ps_exempt_income_ids.unlink()
            res = super(HrPayslip, s_id).unlink()
        return res

    @api.onchange('employee_id', 'date_from', 'date_to')
    def onchange_employee(self):
        res = super(HrPayslip, self).onchange_employee()
        date_from = self.date_from
        date_to = self.date_to
        contract_id = self.contract_id
        if contract_id.date_start and\
                contract_id.date_start.month == date_from.month and\
                contract_id.date_start.year == date_from.year:
            date_from = contract_id.date_start
        if contract_id.date_end and\
                contract_id.date_end.month == date_to.month and\
                contract_id.date_end.year == date_to.year:
            date_to = contract_id.date_end
        values = {
            'eps_id': self.employee_id.eps_id.id,
            'pension_fund_id': self.employee_id.pension_fund_id.id,
            'unemployment_fund_id': self.employee_id.unemployment_fund_id.id,
            'arl_id': self.employee_id.arl_id.id,
            'prepaid_medicine_id': self.employee_id.prepaid_medicine_id.id,
            'afc_id': self.employee_id.afc_id.id,
            'voluntary_contribution_id':
            self.employee_id.voluntary_contribution_id.id,
            'voluntary_contribution2_id':
            self.employee_id.voluntary_contribution2_id.id,
            'bank_account_id': self.employee_id.bank_account_id.id,
            'date_from': date_from,
            'date_to': date_to,
        }
        self.update(values)
        return res

    @api.model
    def create(self, vals):
        if self._context.get('transfer_data', '') and not vals.get(
                'employee_id', ''):
            return False
        employee_id = self.env['hr.employee'].browse(vals.get('employee_id'))
        vals.update({
            'eps_id': employee_id.eps_id.id,
            'pension_fund_id': employee_id.pension_fund_id.id,
            'unemployment_fund_id': employee_id.unemployment_fund_id.id,
            'arl_id': employee_id.arl_id.id,
            'prepaid_medicine_id': employee_id.prepaid_medicine_id.id,
            'afc_id': employee_id.afc_id.id,
            'voluntary_contribution_id':
            employee_id.voluntary_contribution_id.id,
            'voluntary_contribution2_id':
            employee_id.voluntary_contribution2_id.id,
            'bank_account_id': employee_id.bank_account_id.id,
        })
        return super(HrPayslip, self).create(vals)

    @api.multi
    def action_update_entities(self):
        vals = {
            'eps_id': self.employee_id.eps_id.id,
            'pension_fund_id': self.employee_id.pension_fund_id.id,
            'unemployment_fund_id': self.employee_id.unemployment_fund_id.id,
            'arl_id': self.employee_id.arl_id.id,
            'prepaid_medicine_id': self.employee_id.prepaid_medicine_id.id,
            'afc_id': self.employee_id.afc_id.id,
            'voluntary_contribution_id':
            self.employee_id.voluntary_contribution_id.id,
            'voluntary_contribution2_id':
            self.employee_id.voluntary_contribution2_id.id,
        }
        self.write(vals)

    @api.model
    def get_worked_day_lines(self, contracts, date_from, date_to):
        """Overwrite."""
        res = []
        # fill only if the contract as a working schedule linked
        tz_name = self._context.get('tz') or self.env.user.tz or 'UTC'
        if not contracts and self.contract_id:
            contracts = self.contract_id
        contract_id = contracts
        for contract in contracts.filtered(
                lambda contract: contract.resource_calendar_id):
            day_from = datetime.combine(
                fields.Date.from_string(date_from), time.min)
            day_to = datetime.combine(
                fields.Date.from_string(date_to), time.max)
            contract_id = contract

            # compute contract finish before generate payroll
            ct_id = self.contract_completion_id
            if ct_id and ct_id.date.month != self.date_from.month and\
                    ct_id.date <= self.date_to:
                days_pending = 0
                start_date = ct_id.date
                end_date = self.date_from
                diff = relativedelta(end_date, start_date)
                if ct_id.date.month == 2:
                    if calendar.monthrange(ct_id.date.year,
                                           ct_id.date.month)[1] == 28:
                        days_pending = -2
                    else:
                        days_pending = -1
                if self.date_from.month in (1, 2, 4, 6, 8, 9, 11):
                    days_pending = 1
                days_pending += diff.days * -1 + 1
                if start_date == (end_date + relativedelta(days=-1)):
                    days_pending = 0
                hour_pending = days_pending * 8
                attendances = {
                    'name': _("Normal Working Days paid at 100%"),
                    'sequence': 1,
                    'code': 'WORK100',
                    'number_of_days': days_pending,
                    'number_of_hours': hour_pending,
                    'contract_id': contract_id.id,
                }
                res.append(attendances)
                return res

            # compute leave days
            leaves = {}
            calendar_type = contract.resource_calendar_id
            tz = timezone(calendar_type.tz)
            day_leave_intervals = contract.employee_id.list_leaves_payroll(
                day_from, day_to, calendar=contract.resource_calendar_id)
            for day, hours, leave in day_leave_intervals:
                holiday = leave.holiday_id
                current_leave_struct = leaves.setdefault(
                    holiday.holiday_status_id, {
                        'name': holiday.holiday_status_id.name or _(
                            'Global Leaves'),
                        'sequence': 5,
                        'code': holiday.holiday_status_id.name or 'GLOBAL',
                        'number_of_days': 0.0,
                        'number_of_hours': 0.0,
                        'contract_id': contract.id,
                    })
                current_leave_struct['number_of_hours'] += hours
                work_hours = calendar_type.get_work_hours_count(
                    tz.localize(datetime.combine(day, time.min)),
                    tz.localize(datetime.combine(day, time.max)),
                    compute_leaves=False,
                )
                if work_hours:
                    current_leave_struct[
                        'number_of_days'] += hours / work_hours
            # compute worked days
            work_data = contract.employee_id.get_work_days_data(
                day_from, day_to, calendar=contract.resource_calendar_id)
            attendances = {
                'name': _("Normal Working Days paid at 100%"),
                'sequence': 1,
                'code': 'WORK100',
                'number_of_days': work_data['days'],
                'number_of_hours': work_data['hours'],
                'contract_id': contract.id,
            }
            res.append(attendances)
            res.extend(leaves.values())
        is_vacation_pay_31 = False
        from_date = date_from
        to_date = date_to
        if contract_id.date_start and\
                contract_id.date_start.month == from_date.month and\
                contract_id.date_start.year == from_date.year:
            date_from = contract_id.date_start
        if contract_id.date_end and\
                contract_id.date_end.month == to_date.month and\
                contract_id.date_end.year == to_date.year:
            date_to = contract_id.date_end
        if date_from and date_to and\
                contract_id.resource_calendar_id.fix_days:
            leave_days = 0
            total_days = 0
            is_vacation_pay_31 = False
            from_date_from = str(date_from)
            from_date_to = str(date_to)
            self.env.cr.execute(
                """select id from hr_leave where employee_id = %s and ((
                (%s between TO_CHAR(request_date_from,'YYYY-MM-DD') and
                TO_CHAR(request_date_to,'YYYY-MM-DD')) or (%s between
                TO_CHAR(request_date_from,'YYYY-MM-DD') and TO_CHAR(
                request_date_to,'YYYY-MM-DD'))) or((TO_CHAR(
                request_date_from,'YYYY-MM-DD') between %s and %s) or(
                TO_CHAR(request_date_to,'YYYY-MM-DD') between %s and %s)
                and state NOT IN ('draft', 'cancel', 'refuse')))""",
                (contract_id.employee_id.id, from_date_from, from_date_to,
                    from_date_from, from_date_to, from_date_from,
                    from_date_to))
            day_additional = 0
            start_date = fields.Date.to_string(date_from.replace(day=1))
            end_date = fields.Date.to_string((date_from + relativedelta(
                months=+1, day=1, days=-1)))
            for leave_rec in self.env.cr.fetchall():
                leave = self.env['hr.leave'].browse(leave_rec)
                context_start = leave.request_date_from
                # If no comment the process de 2 novelties diferent not is done
                #day_additional = 0
                if not leave.holiday_status_id.no_count_in_payroll:
                    if leave.request_unit_half:
                        leave_days += 0.5
                    if leave.holiday_status_id.vacation_pay_31 and\
                            context_start.month in [1, 3, 5, 7, 8, 10, 12]:
                        if leave.request_date_to >=\
                            leave.request_date_from.replace(day=31) and\
                                date_to ==\
                                leave.request_date_from.replace(day=31) and\
                                not leave.after_close:
                            day_additional = 1
                    if leave.request_date_to.month ==\
                            leave.request_date_from.month and\
                            not leave.after_close:
                        if leave.holiday_status_id.request_unit == 'hour':
                            leave_days += (leave.number_of_days)
                        else:
                            leave_days += ((leave.request_date_to -
                                            leave.request_date_from).days + 1)
                    if leave.request_date_to.month !=\
                            leave.request_date_from.month:
                        if leave.request_date_from > date_from and\
                                leave.request_date_to < date_to:
                            leave_days += ((leave.request_date_to -
                                            leave.request_date_from).days + 1)
                        if leave.request_date_from > date_from and\
                                leave.request_date_to > date_to and\
                                not leave.after_close:
                            leave_days += ((date_to -
                                            leave.request_date_from).days)
                            # Review process when payslip no start in firts day
                            if date_to.month not in [2, 4, 6, 9, 11] and\
                                    self.date_to == date_to.replace(
                                        day=31) and\
                                    leave.request_date_to > self.date_to and\
                                    leave.holiday_status_id.vacation_pay_31:
                                leave_days += 1
                            elif str(date_to) < end_date:
                                leave_days += 1
                        if leave.request_date_from <= date_from and\
                                leave.request_date_to > date_to:
                            leave_days += ((date_to -
                                            date_from).days + 1)
                            if leave_days >= 30:
                                leave_days = 30
                        if leave.request_date_from < date_from and\
                                leave.request_date_to < date_to:
                            leave_days += ((leave.request_date_to -
                                            date_from).days + 1)
            if str(date_from) == start_date and\
                    str(date_to) == end_date:
                total_days = 30
            elif str(date_to) == end_date:
                if date_to.month == 2:
                    if date_to.day == 28:
                        total_days = (date_to - date_from).days + 3
                    else:
                        total_days = (date_to - date_from).days + 2
                else:
                    date_to = date_to.replace(day=30)
                    total_days = (date_to - date_from).days + 1
            else:
                total_days = (date_to - date_from).days + 1
            if start_date == end_date:
                total_days = 1
            for r in res:
                if r['code'] == 'WORK100':
                    r['number_of_days'] = total_days - \
                        leave_days + day_additional
                    r['number_of_hours'] = (total_days - leave_days) *\
                        contract_id.resource_calendar_id.hours_per_day
        if contract_id.leave_generate_id.\
                leave_id.vacation_pay_31 and contract_id.\
                leave_generate_id.days > 31:
            raise ValidationError(_(
                'Maximum 31 days should allow in the case of Vacation Pay 31'
                ' in Leave Generate.'))
        if contract_id.date_start and date_from and\
                contract_id.date_start.month == date_from.month and\
                contract_id.date_start.year == date_from.year:
            date_from = contract_id.date_start
        if next((item for item in res if item["code"] == "GLOBAL"), False):
            res = [items for items in res if not ("GLOBAL" == items.get(
                'code', ''))]
        from_date_from = str(date_from)
        from_date_to = str(date_to)
        if contract_id.employee_id:
            self.env.cr.execute(
                """select id from hr_leave where employee_id = %s and ((
                (%s between TO_CHAR(request_date_from,'YYYY-MM-DD') and
                TO_CHAR(request_date_to,'YYYY-MM-DD')) or (%s between
                TO_CHAR(request_date_from,'YYYY-MM-DD') and TO_CHAR(
                request_date_to,'YYYY-MM-DD'))) or((TO_CHAR(
                request_date_from,'YYYY-MM-DD') between %s and %s) or(
                TO_CHAR(request_date_to,'YYYY-MM-DD') between %s and %s)
                and state NOT IN ('draft', 'cancel', 'refuse')))""",
                (contract_id.employee_id.id, from_date_from, from_date_to,
                    from_date_from, from_date_to, from_date_from,
                    from_date_to))
        leave_line = {}
        leave_yes_total = 0.0
        for leave_rec in self.env.cr.fetchall():
            leave = self.env['hr.leave'].browse(leave_rec)
            if not leave.holiday_status_id.no_count_in_payroll:
                day_additional = 0
                leave_days = 0
                context_start = leave.request_date_from
                if leave.holiday_status_id.vacation_pay_31 and\
                        context_start.month in [1, 3, 5, 7, 8, 10, 12]:
                    if leave.request_date_to >=\
                        leave.request_date_from.replace(day=31) and\
                            date_to ==\
                            leave.request_date_from.replace(day=31)and\
                            date_to < leave.request_date_to and\
                            not leave.after_close:
                        day_additional = 0
                if leave.request_date_to.month ==\
                        leave.request_date_from.month and\
                        not leave.after_close:
                    if leave.holiday_status_id.request_unit == 'hour':
                        leave_days += (leave.number_of_days)
                    else:
                        leave_days += ((leave.request_date_to -
                                        leave.request_date_from).days + 1)
                if leave.request_date_to.month !=\
                        leave.request_date_from.month:
                    day_additional = 0
                    if leave.request_date_from > date_from and\
                            leave.request_date_to < date_to:
                        leave_days = ((leave.request_date_to -
                                       leave.request_date_from).days + 1)
                    if leave.request_date_from > date_from and\
                            leave.request_date_to > date_to and\
                            not leave.after_close:
                        leave_days = ((date_to -
                                       leave.request_date_from).days)
                        # Review process when payslip no start in firts day
                        if date_to.month not in [2, 4, 6, 9, 11] and\
                                self.date_to == date_to.replace(day=31) and\
                                leave.request_date_to > self.date_to and\
                                leave.holiday_status_id.vacation_pay_31:
                            leave_days += 1
                        elif str(date_to) < end_date:
                            leave_days += 1
                    if leave.request_date_from <= date_from and\
                            leave.request_date_to > date_to:
                        leave_days = ((date_to -
                                       date_from).days + 1)
                        if leave_days >= 30:
                            leave_days = 30
                    if leave.request_date_from < date_from and\
                            leave.request_date_to < date_to:
                        leave_days = ((leave.request_date_to -
                                       date_from).days + 1)
                if not leave_line.get(leave.holiday_status_id.name, ''):
                    leave_line.update(
                        {leave.holiday_status_id.name: leave_days +
                         day_additional})
                else:
                    total_days = leave_line.get(
                        leave.holiday_status_id.name, '')
                    leave_line.update({
                        leave.holiday_status_id.name: total_days
                        + leave_days + day_additional})
                if leave.holiday_status_id.is_sumar_en_nomina:
                    leave_yes_total += leave_days
        if leave_line:
            for key, value in leave_line.items():
                res.append({
                    'name': key,
                    'code': key,
                    'number_of_days': value,
                    'number_of_hours':
                    contract_id.resource_calendar_id.hours_per_day *
                    value,
                    'contract_id': contract_id.id})
        if leave_yes_total > 0:
            work100_val = next((item for item in res if item[
                "code"] == "WORK100"), False)
            work100_val.update(
                {'number_of_days': leave_yes_total + work100_val.get(
                    'number_of_days', '')})
        if is_vacation_pay_31 and next((item for item in res if item[
                "code"] == "WORK100"), False):
            work100_val = next((item for item in res if item[
                "code"] == "WORK100"), False)
            work100_val.update(
                {'number_of_days': 1.0 + work100_val.get(
                    'number_of_days', '')})
        return res

    @api.onchange('contract_id')
    def onchange_contract(self):
        super(HrPayslip, self).onchange_contract()
        self.journal_id = self.env['account.journal'].search(
            [('name', 'like', '%NOMINA%')], limit=1).id


class HrPayslipWorkedDays(models.Model):
    _inherit = 'hr.payslip.worked_days'

    @api.model
    def create(self, vals):
        if self._context.get('transfer_data', '') and not vals.get(
                'payslip_id', '') or not vals.get('contract_id', ''):
            return False
        return super(HrPayslipWorkedDays, self).create(vals)

    employee_id = fields.Many2one(
        'hr.employee', related='payslip_id.employee_id', store=1)
    description = fields.Text('Description Details')

    @api.multi
    def write(self, vals):
        res = super(HrPayslipWorkedDays, self).write(vals)
        if self.code == 'WORK100' and\
                vals.get('number_of_days', '') and\
                self.payslip_id.contract_id.resource_calendar_id.fix_days:
            raise ValidationError(_(
                'Number of days should be change.'))
        return res
