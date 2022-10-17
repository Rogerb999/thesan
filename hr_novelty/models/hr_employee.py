# -*- coding: utf-8 -*-

import datetime
import calendar
from datetime import timedelta

from odoo import models, api, fields, _
import math


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    total_remaining_approve_novelty = fields.Integer(
        'Total Remaining Approve Novelty',
        compute='_compute_total_remaining_approve_novelty')

    @api.multi
    def _compute_total_remaining_approve_novelty(self):
        novelty_obj = self.env['hr.novelty']
        for record in self:
            record.total_remaining_approve_novelty = novelty_obj.search_count([
                ('employee_id.parent_id', '=', record.id),
                ('state', 'in', ['wait_comments', 'wait'])])

    @api.multi
    def view_novelty_records(self):
        novelty_ids = self.env['hr.novelty'].search([
            ('employee_id.parent_id', '=', self.id),
            ('state', 'in', ['wait', 'wait_comments'])])
        return {
            'name': _('Novelty'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'hr.novelty',
            'domain': [('id', '=', novelty_ids.ids)],
            'type': 'ir.actions.act_window',
        }

    @api.multi
    def round1(self, amount):
        return round(amount)

    @api.multi
    def round100(self, amount):
        result = int(math.ceil(amount / 100.0)) * 100
        return result

    @api.multi
    def round1000(self, amount):
        return round(amount, -3)

    @api.multi
    def round2d(self, amount):
        return round(amount, 2)

    @api.multi
    def get_novelties(self, date_to_payroll, event):
        """Get novelty of current month and previous month approved."""
        event_id = self.env['hr.novelty.event'].search([('name', '=', event)])
        tz_name = self._context.get('tz') or self.env.user.tz or 'UTC'
        amount = 0
        if event_id:
            novelty_ids = self.env['hr.novelty'].search(
                [('employee_id', '=', self.id),
                 ('event_id', '=', event_id.id),
                 ('state', '=', 'approved')])
            date_from_payroll = datetime.date(
                date_to_payroll.year, date_to_payroll.month, 1)
            for novelty in novelty_ids:
                if event_id.subtype_id.name == 'Ocasional':
                    if date_to_payroll and novelty.start_date:
                        date_payroll = fields.Datetime.from_string(
                            date_to_payroll)
                        date_payroll = date_payroll.replace(hour=11, minute=59)
                        start_date = fields.Datetime.from_string(
                            novelty.start_date)
                        date_from_payroll = fields.Datetime.from_string(
                            date_from_payroll)
                        if start_date <= date_payroll and\
                                start_date >= date_from_payroll and\
                                not novelty.after_close:
                            if event_id.affectation == 'deduction':
                                amount += (novelty.amount * -1)
                            else:
                                amount += novelty.amount
                elif event_id.subtype_id.name == 'Fija':
                    if date_to_payroll and novelty.start_date and\
                        novelty.end_date and\
                            not novelty.after_close:
                        date_payroll = fields.Datetime.from_string(
                            date_to_payroll)
                        start_date = fields.Datetime.from_string(
                            novelty.start_date)
                        end_date = fields.Datetime.from_string(
                            novelty.end_date)
                        if start_date <= date_payroll and\
                                end_date >= date_payroll:
                            if event_id.affectation == 'deduction':
                                amount += (novelty.amount * -1)
                            else:
                                amount += novelty.amount
                    elif date_to_payroll and novelty.start_date and not\
                        novelty.end_date and\
                            not novelty.after_close:
                        date_payroll = fields.Datetime.from_string(
                            date_to_payroll)
                        start_date = fields.Datetime.from_string(
                            novelty.start_date)
                        if start_date <= date_payroll:
                            if event_id.affectation == 'deduction':
                                amount += (novelty.amount * -1)
                            else:
                                amount += novelty.amount
            return amount
        else:
            return 0.0

    @api.multi
    def get_acumulate_month_before(self, date, configuration):
        """Function to fetch previous month acumulate."""
        conf_id = self.env['hr.conf.acumulated'].search(
            [('name', '=', configuration)])
        result = 0
        if date.month != 1:
            date1 = fields.Date.from_string(date)
            if conf_id:
                last_day_of_prev_month = date1.replace(
                    day=1) - timedelta(days=1)
                start_day_of_prev_month = date1.replace(
                    day=1) - timedelta(days=last_day_of_prev_month.day)
                payslips = self.env['hr.payslip'].search(
                    [('date_from', '>=', start_day_of_prev_month),
                     ('date_to', '<=', last_day_of_prev_month),
                     ('employee_id', '=', self.id)])
                if not payslips:
                    payslips = self.env['hr.payslip'].search(
                        [('date_from', '<=', last_day_of_prev_month),
                         ('date_to', '<=', last_day_of_prev_month),
                         ('employee_id', '=', self.id)])
                acumulate_employee_ids = self.env[
                    'hr.employee.acumulate'].search(
                    [('employee_id', '=', self.id),
                     ('hr_rules_acumulate_id', '=', conf_id.id),
                     ('pay_slip_id', 'in', payslips.ids)
                     ])
                if acumulate_employee_ids:
                    for acumulate in acumulate_employee_ids:
                        result += acumulate.total_acumulate
        return result

    @api.multi
    def get_year_accumulate(self, configuration):
        """Function to fetch year accumulate."""
        conf_id = self.env['hr.conf.acumulated'].search(
            [('name', '=', configuration)])
        result = 0
        if conf_id:
            payslips = self.env['hr.payslip'].search(
                [('employee_id', '=', self.id)])
            accumulate_employee_ids = self.env['hr.employee.acumulate'].search(
                [('employee_id', '=', self.id),
                 ('hr_rules_acumulate_id', '=', conf_id.id),
                 ('pay_slip_id', 'in', payslips.ids)
                 ])
            for accumulate in accumulate_employee_ids:
                result += accumulate.total_acumulate
        return result

    @api.multi
    def get_value_line_payslip_before(self, payslip, rules, month=12, year=0):
        """Function to fetch year accumulate month before."""
        result = 0
        if payslip.date_from.month == 1:
            year = payslip.date_from.year - 1
            month = 12
        elif payslip.date_from.month == 7:
            year = payslip.date_from.year
            month = 6
        else:
            year = payslip.date_from.year
            month = payslip.date_from.month - 1
        date = payslip.date_from.replace(day=15, month=month, year=year)
        payslip = self.env['hr.payslip'].search([
            ('employee_id', '=', self.id),
            ('date_from', '<=', date),
            ('date_to', '>=', date)
        ])
        if payslip.line_ids:
            for line in payslip.line_ids:
                if line.salary_rule_id.name in (rules):
                    result += line.total
        return result

    @api.multi
    def get_average_paid_annual_or_wage(self, date, payslip, list_categ):
        """Function obtain summatory salary with basic category."""
        result = 0
        accum_salary = 0
        accum_month = 0
        add_month_actual = True
        if payslip.contract_id.father_contract_id:
            if payslip.contract_id.father_contract_id.date_end == date:
                add_month_actual = False
        payslip_now = self.env['hr.payslip'].search(
            [('id', '=', payslip.id)])
        date1 = fields.Date.from_string(date)
        result_days = sum([work_days.number_of_days for work_days
                           in payslip_now.worked_days_line_ids])
        if date1:
            last_day_of_prev_month = date1.replace(day=1)
            start_day_of_prev_month = date1.replace(month=1, day=1)
            payslips = self.env['hr.payslip'].search(
                [('date_from', '>=', start_day_of_prev_month),
                 ('date_to', '<=', last_day_of_prev_month),
                 ('employee_id', '=', self.id),
                 ('state', 'in', ('done', 'paid'))])
            for p_id in payslips:
                for line in p_id.line_ids:
                    if line.salary_rule_id.category_id.code in (list_categ)\
                            and not\
                            line.slip_id.contract_id.exclude_from_seniority:
                        accum_salary += line.total
            if add_month_actual:
                for p_id in payslip_now:
                    for line in p_id.ps_input_rf_ids:
                        if line.rule_id.category_id.code in (list_categ):
                            accum_month += line.value_final
            days_exclude = 0
            leaves_type_ids = self.env['hr.leave.type'].search([
                ('exclude_calculate_payslip', '=', True)])
            for leave_type in leaves_type_ids:
                worked_days_line_ids = self.env[
                    'hr.payslip.worked_days'].search([
                        ('payslip_id', '=', payslip.id),
                        ('code', '=', leave_type.name)])
                days_exclude += sum([work_days.number_of_days for work_days
                                     in worked_days_line_ids])
            result_days -= days_exclude
            if result_days > 30:
                result_days = 30
            accum_month = (accum_month / 30) * result_days
            accum_salary += accum_month
        result = accum_salary
        # Calculate before three months is the same salary Basic
        last_day_of_prev_month = date1.replace(
            day=1) + datetime.timedelta(days=-1)
        auxmonthbegin = 1
        if payslip.date_from.month > 3:
            auxmonthbegin = payslip.date_from.month - 3
        start_day_of_prev_month = date1.replace(month=(auxmonthbegin), day=1)
        payslips = self.env['hr.payslip'].search(
            [('date_from', '>=', start_day_of_prev_month),
             ('date_to', '<=', last_day_of_prev_month),
             ('employee_id', '=', self.id),
             ('state', 'in', ('done', 'paid'))])
        auxmonths = 0
        valmonthbefore = 0
        accum_month = 0
        for p_id in payslip_now:
            for line in p_id.ps_input_rf_ids:
                if line.rule_id.category_id.code in (list_categ):
                    accum_month += line.value_final
        result_days = sum([work_days.number_of_days for work_days
                           in payslip_now.worked_days_line_ids])
        '''
        if result_days >= 30:
            result_days = 30
        else:
            accum_month = (accum_month/result_days)*30'''
        for p_id in payslips:
            acc_salary = 0
            for line in p_id.line_ids:
                if line.salary_rule_id.category_id.code in (list_categ)\
                        and not\
                        line.slip_id.contract_id.exclude_from_seniority:
                    acc_salary += line.total
            if valmonthbefore == round(accum_month) and\
                    acc_salary == valmonthbefore:
                acc_salary = (acc_salary / 30) * \
                    self.get_days_annual(payslip.date_to)
                result = acc_salary
            valmonthbefore = acc_salary
        return result

    @api.multi
    def get_average_paid_annual_less_pay31(self, date, payslip, list_categ):
        """Function obtain summatory salary with basic category."""
        result = 0
        accum_salary = 0
        accum_month = 0
        add_month_actual = True
        if payslip.contract_id.father_contract_id:
            if payslip.contract_id.father_contract_id.date_end == date:
                add_month_actual = False
        payslip_now = self.env['hr.payslip'].search(
            [('id', '=', payslip.id)])
        date1 = fields.Date.from_string(date)
        result_days = sum([work_days.number_of_days for work_days
                           in payslip_now.worked_days_line_ids])
        if date1:
            last_day_of_prev_month = date1.replace(day=1)
            start_day_of_prev_month = date1.replace(month=1, day=1)
            payslips = self.env['hr.payslip'].search(
                [('date_from', '>=', start_day_of_prev_month),
                 ('date_to', '<=', last_day_of_prev_month),
                 ('employee_id', '=', self.id),
                 ('state', 'in', ('done', 'paid'))])
            for p_id in payslips:
                for line in p_id.line_ids:
                    if line.salary_rule_id.category_id.code in (list_categ)\
                            and not\
                            line.slip_id.contract_id.exclude_from_seniority:
                        accum_salary += line.total
                if p_id.date_to.month in [1, 3, 5, 7, 8, 10, 12] and\
                        p_id.date_to.day == 31:
                    leave_id = self.env['hr.leave'].search(
                        [('request_date_from', '<=', p_id.date_to),
                         ('request_date_to', '>=', p_id.date_to),
                         ('employee_id', '=', self.id),
                         ('state', '=', 'validate')])
                    if leave_id and \
                            leave_id.holiday_status_id.vacation_pay_31:
                        accum_salary = accum_salary -\
                            p_id.contract_id.fix_wage_amount / 30
            if add_month_actual:
                for p_id in payslip_now:
                    for line in p_id.ps_input_rf_ids:
                        if line.rule_id.category_id.code in (list_categ):
                            accum_month += line.value_final
                    if p_id.date_to.month in [1, 3, 5, 7, 8, 10, 12] and\
                            p_id.date_to.day == 31:
                        leave_id = self.env['hr.leave'].search(
                            [('request_date_from', '<=', p_id.date_to),
                             ('request_date_to', '>=', p_id.date_to),
                             ('employee_id', '=', self.id),
                             ('state', '=', 'validate')])
                        if leave_id and \
                                leave_id.holiday_status_id.vacation_pay_31:
                            accum_month = accum_month - \
                                p_id.contract_id.fix_wage_amount / 30
            days_exclude = 0
            leaves_type_ids = self.env['hr.leave.type'].search([
                ('exclude_calculate_payslip', '=', True)])
            for leave_type in leaves_type_ids:
                worked_days_line_ids = self.env[
                    'hr.payslip.worked_days'].search([
                        ('payslip_id', '=', payslip.id),
                        ('code', '=', leave_type.name)])
                days_exclude += sum([work_days.number_of_days for work_days
                                     in worked_days_line_ids])
            result_days -= days_exclude
            # if days_exclude != 0 or result_days < 30 and result_days > 0:
            #    if result_days > 30:
            #        result_days = 30
            #    accum_month = (accum_month/30)*result_days
            # if result_days < 0 and accum_month > 0:
            #    accum_month = (accum_month/30)*result_days
            if result_days > 30:
                result_days = 30
            accum_month = (accum_month / 30) * result_days
            accum_salary += accum_month
        result = accum_salary
        last_day_of_prev_month = date1.replace(
            day=1) + datetime.timedelta(days=-1)
        auxmonthbegin = 1
        if payslip.date_from.month > 3:
            auxmonthbegin = payslip.date_from.month - 3
        start_day_of_prev_month = date1.replace(month=(auxmonthbegin), day=1)
        payslips = self.env['hr.payslip'].search(
            [('date_from', '>=', start_day_of_prev_month),
             ('date_to', '<=', last_day_of_prev_month),
             ('employee_id', '=', self.id),
             ('state', 'in', ('done', 'paid'))])
        auxmonths = 0
        valmonthbefore = 0
        accum_month = 0
        if self.entry_date.year == payslip.date_to.year and\
                self.entry_date.month > auxmonthbegin:
            return result
        for p_id in payslip_now:
            for line in p_id.ps_input_rf_ids:
                if line.rule_id.category_id.code in (list_categ):
                    accum_month += line.value_final
            if p_id.date_to.month in [1, 3, 5, 7, 8, 10, 12] and\
                    p_id.date_to.day == 31:
                leave_id = self.env['hr.leave'].search(
                    [('request_date_from', '<=', p_id.date_to),
                     ('request_date_to', '>=', p_id.date_to),
                     ('employee_id', '=', self.id),
                     ('state', '=', 'validate')])
                if leave_id and \
                        leave_id.holiday_status_id.vacation_pay_31:
                    accum_month = round(accum_month -
                                        p_id.contract_id.fix_wage_amount / 30)
        result_days = sum([work_days.number_of_days for work_days
                           in payslip_now.worked_days_line_ids])
        auxmonth = 0
        for p_id in payslips:
            acc_salary = 0
            days_month = 1
            days_month_entry = 1
            if p_id.date_to.year == self.entry_date.year and\
                    p_id.date_to.month == self.entry_date.month:
                days_month_entry = sum([work_days.number_of_days for work_days
                                        in p_id.worked_days_line_ids])
                days_month = 30
            for line in p_id.line_ids:
                if line.salary_rule_id.category_id.code in (list_categ)\
                        and not\
                        line.slip_id.contract_id.exclude_from_seniority:
                    acc_salary += round((line.total /
                                         days_month_entry) * (days_month))
            if p_id.date_to.month in [1, 3, 5, 7, 8, 10, 12] and\
                    p_id.date_to.day == 31:
                leave_id = self.env['hr.leave'].search(
                    [('request_date_from', '<=', p_id.date_to),
                     ('request_date_to', '>=', p_id.date_to),
                     ('employee_id', '=', self.id),
                     ('state', '=', 'validate')])
                if leave_id and \
                        leave_id.holiday_status_id.vacation_pay_31:
                    acc_salary = round(acc_salary -
                                       p_id.contract_id.fix_wage_amount / 30)
            accum_month = round(accum_month, -1)
            valmonthbefore = round(valmonthbefore, -1)
            acc_salary = round(acc_salary, -1)
            if acc_salary == valmonthbefore:
                auxmonth += 1
            if valmonthbefore == round(accum_month) and \
                    acc_salary == valmonthbefore and auxmonth == 2:
                acc_salary = (acc_salary / 30) * \
                    self.get_days_annual(payslip.date_to)
                result = acc_salary
            valmonthbefore = acc_salary
        return result


    @api.multi
    def get_average_paid_annual_less_pay31_without_prom(self, date, payslip, list_categ):
        """Function obtain summatory salary with basic category."""
        result = 0
        accum_salary = 0
        accum_month = 0
        add_month_actual = True
        if payslip.contract_id.father_contract_id:
            if payslip.contract_id.father_contract_id.date_end == date:
                add_month_actual = False
        payslip_now = self.env['hr.payslip'].search(
            [('id', '=', payslip.id)])
        date1 = fields.Date.from_string(date)
        result_days = sum([work_days.number_of_days for work_days
                           in payslip_now.worked_days_line_ids])
        if date1:
            last_day_of_prev_month = date1.replace(day=1)
            start_day_of_prev_month = date1.replace(month=1, day=1)
            payslips = self.env['hr.payslip'].search(
                [('date_from', '>=', start_day_of_prev_month),
                 ('date_to', '<=', last_day_of_prev_month),
                 ('employee_id', '=', self.id),
                 ('state', 'in', ('done', 'paid'))])
            for p_id in payslips:
                for line in p_id.line_ids:
                    if line.salary_rule_id.category_id.code in (list_categ)\
                            and not\
                            line.slip_id.contract_id.exclude_from_seniority:
                        accum_salary += line.total
                if p_id.date_to.month in [1, 3, 5, 7, 8, 10, 12] and\
                        p_id.date_to.day == 31:
                    leave_id = self.env['hr.leave'].search(
                        [('request_date_from', '<=', p_id.date_to),
                         ('request_date_to', '>=', p_id.date_to),
                         ('employee_id', '=', self.id),
                         ('state', '=', 'validate')])
                    if leave_id and \
                            leave_id.holiday_status_id.vacation_pay_31:
                        accum_salary = accum_salary -\
                            p_id.contract_id.fix_wage_amount / 30
            if add_month_actual:
                for p_id in payslip_now:
                    for line in p_id.ps_input_rf_ids:
                        if line.rule_id.category_id.code in (list_categ):
                            accum_month += line.value_final
                    if p_id.date_to.month in [1, 3, 5, 7, 8, 10, 12] and\
                            p_id.date_to.day == 31:
                        leave_id = self.env['hr.leave'].search(
                            [('request_date_from', '<=', p_id.date_to),
                             ('request_date_to', '>=', p_id.date_to),
                             ('employee_id', '=', self.id),
                             ('state', '=', 'validate')])
                        if leave_id and \
                                leave_id.holiday_status_id.vacation_pay_31:
                            accum_month = accum_month - \
                                p_id.contract_id.fix_wage_amount / 30
            days_exclude = 0
            leaves_type_ids = self.env['hr.leave.type'].search([
                ('exclude_calculate_payslip', '=', True)])
            for leave_type in leaves_type_ids:
                worked_days_line_ids = self.env[
                    'hr.payslip.worked_days'].search([
                        ('payslip_id', '=', payslip.id),
                        ('code', '=', leave_type.name)])
                days_exclude += sum([work_days.number_of_days for work_days
                                     in worked_days_line_ids])
            result_days -= days_exclude
            # if days_exclude != 0 or result_days < 30 and result_days > 0:
            #    if result_days > 30:
            #        result_days = 30
            #    accum_month = (accum_month/30)*result_days
            # if result_days < 0 and accum_month > 0:
            #    accum_month = (accum_month/30)*result_days
            if result_days > 30:
                result_days = 30
            accum_month = (accum_month / 30) * result_days
            accum_salary += accum_month
        result = accum_salary
        return result

    @api.multi
    def get_base_average_paid_annual_less_pay31(
            self, date, payslip, list_categ):
        """Function obtain summatory salary with basic category."""
        result = 0
        accum_salary = 0
        accum_month = 0
        add_month_actual = True
        if self.entry_date >= payslip.date_from:
            return self.get_average_paid_biannual(date, payslip)
        if payslip.contract_id.father_contract_id:
            if payslip.contract_id.father_contract_id.date_end == date:
                add_month_actual = False
        payslip_now = self.env['hr.payslip'].search(
            [('id', '=', payslip.id)])
        date1 = fields.Date.from_string(date)
        result_days = sum([work_days.number_of_days for work_days
                           in payslip_now.worked_days_line_ids])
        if date1:
            last_day_of_prev_month = date1.replace(day=1)
            start_day_of_prev_month = date1.replace(month=1, day=1)
            payslips = self.env['hr.payslip'].search(
                [('date_from', '>=', start_day_of_prev_month),
                 ('date_to', '<=', last_day_of_prev_month),
                 ('employee_id', '=', self.id),
                 ('state', 'in', ('done', 'paid'))])
            for p_id in payslips:
                for line in p_id.line_ids:
                    if line.salary_rule_id.category_id.code in (list_categ)\
                            and not\
                            line.slip_id.contract_id.exclude_from_seniority:
                        accum_salary += line.total
                if p_id.date_to.month in [1, 3, 5, 7, 8, 10, 12] and\
                        p_id.date_to.day == 31:
                    leave_id = self.env['hr.leave'].search(
                        [('request_date_from', '<=', p_id.date_to),
                         ('request_date_to', '>=', p_id.date_to),
                         ('employee_id', '=', self.id),
                         ('state', '=', 'validate')])
                    if leave_id and \
                            leave_id.holiday_status_id.vacation_pay_31:
                        accum_salary = accum_salary -\
                            p_id.contract_id.fix_wage_amount / 30
            if add_month_actual:
                for p_id in payslip_now:
                    for line in p_id.ps_input_rf_ids:
                        if line.rule_id.category_id.code in (list_categ):
                            accum_month += line.value_final
                    if p_id.date_to.month in [1, 3, 5, 7, 8, 10, 12] and\
                            p_id.date_to.day == 31:
                        leave_id = self.env['hr.leave'].search(
                            [('request_date_from', '<=', p_id.date_to),
                             ('request_date_to', '>=', p_id.date_to),
                             ('employee_id', '=', self.id),
                             ('state', '=', 'validate')])
                        if leave_id and \
                                leave_id.holiday_status_id.vacation_pay_31:
                            accum_month = accum_month - \
                                p_id.contract_id.fix_wage_amount / 30
            days_exclude = 0
            leaves_type_ids = self.env['hr.leave.type'].search([
                ('exclude_calculate_payslip', '=', True)])
            for leave_type in leaves_type_ids:
                worked_days_line_ids = self.env[
                    'hr.payslip.worked_days'].search([
                        ('payslip_id', '=', payslip.id),
                        ('code', '=', leave_type.name)])
                days_exclude += sum([work_days.number_of_days for work_days
                                     in worked_days_line_ids])
            result_days -= days_exclude
            # if days_exclude != 0 or result_days < 30 and result_days > 0:
            #    if result_days > 30:
            #        result_days = 30
            #    accum_month = (accum_month/30)*result_days
            # if result_days < 0 and accum_month > 0:
            #    accum_month = (accum_month/30)*result_days
            if result_days > 30:
                result_days = 30
            accum_month = (accum_month / 30) * result_days
            accum_salary += accum_month
        result = accum_salary
        last_day_of_prev_month = date1.replace(
            day=1) + datetime.timedelta(days=-1)
        auxmonthbegin = 1
        if payslip.date_from.month > 3:
            auxmonthbegin = payslip.date_from.month - 3
        start_day_of_prev_month = date1.replace(month=(auxmonthbegin), day=1)
        payslips = self.env['hr.payslip'].search(
            [('date_from', '>=', start_day_of_prev_month),
             ('date_to', '<=', last_day_of_prev_month),
             ('employee_id', '=', self.id),
             ('state', 'in', ('done', 'paid'))])
        auxmonths = 0
        valmonthbefore = 0
        accum_month = 0
        if self.entry_date.year == payslip.date_to.year and\
                self.entry_date.month > auxmonthbegin:
            return result
        for p_id in payslip_now:
            for line in p_id.ps_input_rf_ids:
                if line.rule_id.category_id.code in (list_categ):
                    accum_month += line.value_final
            if p_id.date_to.month in [1, 3, 5, 7, 8, 10, 12] and\
                    p_id.date_to.day == 31:
                leave_id = self.env['hr.leave'].search(
                    [('request_date_from', '<=', p_id.date_to),
                     ('request_date_to', '>=', p_id.date_to),
                     ('employee_id', '=', self.id),
                     ('state', '=', 'validate')])
                if leave_id and \
                        leave_id.holiday_status_id.vacation_pay_31:
                    accum_month = round(accum_month -
                                        p_id.contract_id.fix_wage_amount / 30)
        result_days = sum([work_days.number_of_days for work_days
                           in payslip_now.worked_days_line_ids])
        auxmonth = 0
        for p_id in payslips:
            acc_salary = 0
            days_month = 1
            days_month_entry = 1
            if p_id.date_to.year == self.entry_date.year and\
                    p_id.date_to.month == self.entry_date.month:
                days_month_entry = sum([work_days.number_of_days for work_days
                                        in p_id.worked_days_line_ids])
                days_month = 30
            for line in p_id.line_ids:
                if line.salary_rule_id.category_id.code in (list_categ)\
                        and not\
                        line.slip_id.contract_id.exclude_from_seniority:
                    acc_salary += round((line.total /
                                         days_month_entry) * (days_month))
            if p_id.date_to.month in [1, 3, 5, 7, 8, 10, 12] and\
                    p_id.date_to.day == 31:
                leave_id = self.env['hr.leave'].search(
                    [('request_date_from', '<=', p_id.date_to),
                     ('request_date_to', '>=', p_id.date_to),
                     ('employee_id', '=', self.id),
                     ('state', '=', 'validate')])
                if leave_id and \
                        leave_id.holiday_status_id.vacation_pay_31:
                    acc_salary = round(acc_salary -
                                       p_id.contract_id.fix_wage_amount / 30)
            accum_month = round(accum_month, -1)
            valmonthbefore = round(valmonthbefore, -1)
            acc_salary = round(acc_salary, -1)
            if acc_salary == valmonthbefore:
                auxmonth += 1
            if valmonthbefore == round(accum_month) and \
                    acc_salary == valmonthbefore and auxmonth == 2:
                acc_salary = (acc_salary / 30) * \
                    self.get_days_annual(payslip.date_to)
                result = acc_salary
            valmonthbefore = acc_salary
        return result

    @api.multi
    def get_average_paid_annual(self, date, payslip):
        """Function obtain summatory salary with basic category."""
        result = 0
        accum_salary = 0
        accum_month = 0
        add_month_actual = True
        if payslip.contract_id.father_contract_id:
            if payslip.contract_id.father_contract_id.date_end == date:
                add_month_actual = False
        payslip_now = self.env['hr.payslip'].search(
            [('id', '=', payslip.id)])
        date1 = fields.Date.from_string(date)
        result_days = sum([work_days.number_of_days for work_days
                           in payslip_now.worked_days_line_ids])
        if date1:
            last_day_of_prev_month = date1
            start_day_of_prev_month = date1.replace(month=1, day=1)
            payslips = self.env['hr.payslip'].search(
                [('date_from', '>=', start_day_of_prev_month),
                 ('date_to', '<=', last_day_of_prev_month),
                 ('employee_id', '=', self.id),
                 ('state', 'in', ('done', 'paid'))])
            for p_id in payslips:
                for line in p_id.line_ids:
                    if line.salary_rule_id.category_id.code in (
                        'BASIC', 'AUS', 'AUSINC', 'AUXTRANS')\
                            and not\
                            line.slip_id.contract_id.exclude_from_seniority:
                        accum_salary += line.total
            if add_month_actual:
                for p_id in payslip_now:
                    for line in p_id.ps_input_rf_ids:
                        if line.rule_id.category_id.code in (
                                'BASIC', 'AUS', 'AUSINC', 'AUXTRANS'):
                            accum_month += line.value_final
            days_exclude = 0
            leaves_type_ids = self.env['hr.leave.type'].search([
                ('exclude_calculate_payslip', '=', True)])
            for leave_type in leaves_type_ids:
                worked_days_line_ids = self.env[
                    'hr.payslip.worked_days'].search([
                        ('payslip_id', '=', payslip.id),
                        ('code', '=', leave_type.name)])
                days_exclude += sum([work_days.number_of_days for work_days
                                     in worked_days_line_ids])
            result_days -= days_exclude
            if result_days > 30:
                result_days = 30
            accum_month = (accum_month / 30) * result_days
            accum_salary += accum_month
        result = accum_salary
        return result

    @api.multi
    def get_average_paid_annual_termination(self, date, payslip, list_categ):
        """Function obtain summatory salary with basic category."""
        result = 0
        accum_salary = 0
        accum_month = 0
        add_month_actual = True
        if payslip.contract_id.father_contract_id:
            if payslip.contract_id.father_contract_id.date_end == date:
                add_month_actual = False
            if payslip.state == 'done':
                add_month_actual = False
        payslip_now = self.env['hr.payslip'].search(
            [('id', '=', payslip.id)])
        date1 = fields.Date.from_string(date)
        result_days = sum([work_days.number_of_days for work_days
                           in payslip_now.worked_days_line_ids])
        if date1:
            last_day_of_prev_month = date1.replace(month=12, day=31)
            start_day_of_prev_month = date1.replace(month=1, day=1)
            payslips = self.env['hr.payslip'].search(
                [('date_from', '>=', start_day_of_prev_month),
                 ('date_to', '<=', last_day_of_prev_month),
                 ('employee_id', '=', self.id),
                 ('state', 'in', ('done', 'paid'))])
            for p_id in payslips:
                for line in p_id.line_ids:
                    if line.salary_rule_id.category_id.code in (list_categ)\
                            and not\
                            line.slip_id.contract_id.exclude_from_seniority:
                        accum_salary += line.total
                if p_id.date_to.month in [1, 3, 5, 7, 8, 10, 12] and\
                        p_id.date_to.day == 31:
                    leave_id = self.env['hr.leave'].search(
                        [('request_date_from', '<=', p_id.date_to),
                         ('request_date_to', '>=', p_id.date_to),
                         ('employee_id', '=', self.id),
                         ('state', '=', 'validate')])
                    if leave_id and \
                            leave_id.holiday_status_id.vacation_pay_31:
                        accum_salary = accum_salary -\
                            p_id.contract_id.fix_wage_amount / 30
            if add_month_actual:
                for p_id in payslip_now:
                    for line in p_id.ps_input_rf_ids:
                        if line.rule_id.category_id.code in (list_categ):
                            accum_month += line.value_final
                    if p_id.date_to.month in [1, 3, 5, 7, 8, 10, 12] and\
                            p_id.date_to.day == 31:
                        leave_id = self.env['hr.leave'].search(
                            [('request_date_from', '<=', p_id.date_to),
                             ('request_date_to', '>=', p_id.date_to),
                             ('employee_id', '=', self.id),
                             ('state', '=', 'validate')])
                        if leave_id and \
                                leave_id.holiday_status_id.vacation_pay_31:
                            accum_month = accum_month - \
                                p_id.contract_id.fix_wage_amount / 30
            days_exclude = 0
            leaves_type_ids = self.env['hr.leave.type'].search([
                ('exclude_calculate_payslip', '=', True)])
            for leave_type in leaves_type_ids:
                worked_days_line_ids = self.env[
                    'hr.payslip.worked_days'].search([
                        ('payslip_id', '=', payslip.id),
                        ('code', '=', leave_type.name)])
                days_exclude += sum([work_days.number_of_days for work_days
                                     in worked_days_line_ids])
            result_days -= days_exclude
            if days_exclude != 0 or result_days < 30 and result_days > 0:
                if result_days > 30:
                    result_days = 30
                accum_month = (accum_month / 30) * result_days
            if result_days < 0 and accum_month > 0:
                accum_month = (accum_month / 30) * result_days
            accum_salary += accum_month
        result = accum_salary
        last_day_of_prev_month = date1.replace(
            day=1) + datetime.timedelta(days=-1)
        auxmonthbegin = 1
        if payslip.date_from.month > 3:
            auxmonthbegin = payslip.date_from.month - 3
        start_day_of_prev_month = date1.replace(month=(auxmonthbegin), day=1)
        payslips = self.env['hr.payslip'].search(
            [('date_from', '>=', start_day_of_prev_month),
             ('date_to', '<=', last_day_of_prev_month),
             ('employee_id', '=', self.id),
             ('state', 'in', ('done', 'paid'))])
        auxmonths = 0
        valmonthbefore = 0
        accum_month = 0
        if self.entry_date.year == payslip.date_to.year and\
                self.entry_date.month > auxmonthbegin:
            return result
        for p_id in payslip_now:
            for line in p_id.ps_input_rf_ids:
                if line.rule_id.category_id.code in (list_categ):
                    accum_month += line.value_final
            if p_id.date_to.month in [1, 3, 5, 7, 8, 10, 12] and\
                    p_id.date_to.day == 31:
                leave_id = self.env['hr.leave'].search(
                    [('request_date_from', '<=', p_id.date_to),
                     ('request_date_to', '>=', p_id.date_to),
                     ('employee_id', '=', self.id),
                     ('state', '=', 'validate')])
                if leave_id and \
                        leave_id.holiday_status_id.vacation_pay_31:
                    accum_month = round(accum_month -
                                        p_id.contract_id.fix_wage_amount / 30)
        result_days = sum([work_days.number_of_days for work_days
                           in payslip_now.worked_days_line_ids])
        auxmonth = 0
        for p_id in payslips:
            acc_salary = 0
            days_month = 1
            days_month_entry = 1
            if p_id.date_to.year == self.entry_date.year and\
                    p_id.date_to.month == self.entry_date.month:
                days_month_entry = sum([work_days.number_of_days for work_days
                                        in p_id.worked_days_line_ids])
                days_month = 30
            for line in p_id.line_ids:
                if line.salary_rule_id.category_id.code in (list_categ)\
                        and not\
                        line.slip_id.contract_id.exclude_from_seniority:
                    acc_salary += round((line.total /
                                         days_month_entry) * (days_month))
            if p_id.date_to.month in [1, 3, 5, 7, 8, 10, 12] and\
                    p_id.date_to.day == 31:
                leave_id = self.env['hr.leave'].search(
                    [('request_date_from', '<=', p_id.date_to),
                     ('request_date_to', '>=', p_id.date_to),
                     ('employee_id', '=', self.id),
                     ('state', '=', 'validate')])
                if leave_id and \
                        leave_id.holiday_status_id.vacation_pay_31:
                    acc_salary = round(acc_salary -
                                       p_id.contract_id.fix_wage_amount / 30)
            if acc_salary == valmonthbefore:
                auxmonth += 1
            if valmonthbefore == round(accum_month) and \
                    acc_salary == valmonthbefore and auxmonth == 2:
                acc_salary = (acc_salary / 30) * \
                    self.get_days_annual(payslip.contract_id.date_end)
                result = acc_salary
            valmonthbefore = acc_salary
        return result


    @api.multi
    def get_average_paid_annual_termination_seq(self, date, payslip, seqs):
        """Function obtain summatory salary with basic category."""
        result = 0
        accum_salary = 0
        accum_month = 0
        add_month_actual = True
        if payslip.contract_id.father_contract_id:
            if payslip.contract_id.father_contract_id.date_end == date:
                add_month_actual = False
        payslip_now = self.env['hr.payslip'].search(
            [('id', '=', payslip.id),
             ('state', '=', 'draft')])
        date1 = fields.Date.from_string(date)
        result_days = sum([work_days.number_of_days for work_days
                           in payslip_now.worked_days_line_ids])
        if date1:
            last_day_of_prev_month = date1.replace(month=12, day=31)
            start_day_of_prev_month = date1.replace(month=1, day=1)
            payslips = self.env['hr.payslip'].search(
                [('date_from', '>=', start_day_of_prev_month),
                 ('date_to', '<=', last_day_of_prev_month),
                 ('employee_id', '=', self.id),
                 ('state', 'in', ('done', 'paid'))])
            for p_id in payslips:
                for line in p_id.line_ids:
                    if str(line.salary_rule_id.sequence) in (seqs)\
                            and not\
                            line.slip_id.contract_id.exclude_from_seniority:
                        accum_salary += line.total
                if p_id.date_to.month in [1, 3, 5, 7, 8, 10, 12] and\
                        p_id.date_to.day == 31:
                    leave_id = self.env['hr.leave'].search(
                        [('request_date_from', '<=', p_id.date_to),
                         ('request_date_to', '>=', p_id.date_to),
                         ('employee_id', '=', self.id),
                         ('state', '=', 'validate')])
                    if leave_id and \
                            leave_id.holiday_status_id.vacation_pay_31:
                        accum_salary = accum_salary -\
                            p_id.contract_id.fix_wage_amount / 30
            if add_month_actual:
                for p_id in payslip_now:
                    for line in p_id.ps_input_rf_ids:
                        if str(line.rule_id.sequence) in (seqs):
                            accum_month += line.value_final
                    if p_id.date_to.month in [1, 3, 5, 7, 8, 10, 12] and\
                            p_id.date_to.day == 31:
                        leave_id = self.env['hr.leave'].search(
                            [('request_date_from', '<=', p_id.date_to),
                             ('request_date_to', '>=', p_id.date_to),
                             ('employee_id', '=', self.id),
                             ('state', '=', 'validate')])
                        if leave_id and \
                                leave_id.holiday_status_id.vacation_pay_31:
                            accum_month = accum_month - \
                                p_id.contract_id.fix_wage_amount / 30
            days_exclude = 0
            leaves_type_ids = self.env['hr.leave.type'].search([
                ('exclude_calculate_payslip', '=', True)])
            for leave_type in leaves_type_ids:
                worked_days_line_ids = self.env[
                    'hr.payslip.worked_days'].search([
                        ('payslip_id', '=', payslip.id),
                        ('code', '=', leave_type.name)])
                days_exclude += sum([work_days.number_of_days for work_days
                                     in worked_days_line_ids])
            result_days -= days_exclude
            if days_exclude != 0 or result_days < 30 and result_days > 0:
                if result_days > 30:
                    result_days = 30
                accum_month = (accum_month / 30) * result_days
            if result_days < 0 and accum_month > 0:
                accum_month = (accum_month / 30) * result_days
            accum_salary += accum_month
        result = accum_salary
        last_day_of_prev_month = date1.replace(
            day=1) + datetime.timedelta(days=-1)
        auxmonthbegin = 1
        if payslip.date_from.month > 3:
            auxmonthbegin = payslip.date_from.month - 3
        start_day_of_prev_month = date1.replace(month=(auxmonthbegin), day=1)
        payslips = self.env['hr.payslip'].search(
            [('date_from', '>=', start_day_of_prev_month),
             ('date_to', '<=', last_day_of_prev_month),
             ('employee_id', '=', self.id),
             ('state', 'in', ('done', 'paid'))])
        auxmonths = 0
        valmonthbefore = 0
        accum_month = 0
        if self.entry_date.year == payslip.date_to.year and\
                self.entry_date.month > auxmonthbegin:
            return result
        for p_id in payslip_now:
            for line in p_id.ps_input_rf_ids:
                if str(line.rule_id.sequence) in (seqs):
                    accum_month += line.value_final
            if p_id.date_to.month in [1, 3, 5, 7, 8, 10, 12] and\
                    p_id.date_to.day == 31:
                leave_id = self.env['hr.leave'].search(
                    [('request_date_from', '<=', p_id.date_to),
                     ('request_date_to', '>=', p_id.date_to),
                     ('employee_id', '=', self.id),
                     ('state', '=', 'validate')])
                if leave_id and \
                        leave_id.holiday_status_id.vacation_pay_31:
                    accum_month = round(accum_month -
                                        p_id.contract_id.fix_wage_amount / 30)
        result_days = sum([work_days.number_of_days for work_days
                           in payslip_now.worked_days_line_ids])
        auxmonth = 0
        for p_id in payslips:
            acc_salary = 0
            days_month = 1
            days_month_entry = 1
            if p_id.date_to.year == self.entry_date.year and\
                    p_id.date_to.month == self.entry_date.month:
                days_month_entry = sum([work_days.number_of_days for work_days
                                        in p_id.worked_days_line_ids])
                days_month = 30
            for line in p_id.line_ids:
                if str(line.salary_rule_id.sequence) in (seqs)\
                        and not\
                        line.slip_id.contract_id.exclude_from_seniority:
                    acc_salary += round((line.total /
                                         days_month_entry) * (days_month))
            if p_id.date_to.month in [1, 3, 5, 7, 8, 10, 12] and\
                    p_id.date_to.day == 31:
                leave_id = self.env['hr.leave'].search(
                    [('request_date_from', '<=', p_id.date_to),
                     ('request_date_to', '>=', p_id.date_to),
                     ('employee_id', '=', self.id),
                     ('state', '=', 'validate')])
                if leave_id and \
                        leave_id.holiday_status_id.vacation_pay_31:
                    acc_salary = round(acc_salary -
                                       p_id.contract_id.fix_wage_amount / 30)
            if acc_salary == valmonthbefore:
                auxmonth += 1
            if valmonthbefore == round(accum_month) and \
                    acc_salary == valmonthbefore and auxmonth == 2:
                acc_salary = (acc_salary / 30) * \
                    self.get_days_annual(payslip.contract_id.date_end)
                result = acc_salary
            valmonthbefore = acc_salary
        return result


    @api.multi
    def get_average_paid_biannual_termination(self, date, payslip, list_categ):
        """Function obtain summatory salary with basic category."""
        result = 0
        accum_salary = 0
        accum_month = 0
        add_month_actual = True
        if payslip.contract_id.father_contract_id:
            if payslip.contract_id.father_contract_id.date_end == date:
                add_month_actual = False
        if payslip.state == 'done':
            add_month_actual = False
        payslip_now = self.env['hr.payslip'].search(
            [('id', '=', payslip.id)])
        if date.month == 12 and payslip.date_from.month == 1:
            date1 = fields.Date.from_string(payslip.date_from)
        else:
            date1 = fields.Date.from_string(date)
        result_days = sum([work_days.number_of_days for work_days
                           in payslip_now.worked_days_line_ids])
        if date1:
            if date1.month <= 6:
                last_day_of_prev_month = date1.replace(month=6, day=30)
                start_day_of_prev_month = date1.replace(month=1, day=1)
            else:
                last_day_of_prev_month = date1.replace(month=12, day=31)
                start_day_of_prev_month = date1.replace(month=7, day=1)
            payslips = self.env['hr.payslip'].search(
                [('date_from', '>=', start_day_of_prev_month),
                 ('date_to', '<=', last_day_of_prev_month),
                 ('employee_id', '=', self.id),
                 ('state', 'in', ('done', 'paid'))])
            for p_id in payslips:
                for line in p_id.line_ids:
                    if line.salary_rule_id.category_id.code in (list_categ)\
                            and not\
                            line.slip_id.contract_id.exclude_from_seniority:
                        accum_salary += line.total
            if add_month_actual:
                for p_id in payslip_now:
                    for line in p_id.ps_input_rf_ids:
                        if line.rule_id.category_id.code in (list_categ):
                            accum_month += line.value_final
            days_exclude = 0
            leaves_type_ids = self.env['hr.leave.type'].search([
                ('exclude_calculate_payslip', '=', True)])
            for leave_type in leaves_type_ids:
                worked_days_line_ids = self.env[
                    'hr.payslip.worked_days'].search([
                        ('payslip_id', '=', payslip.id),
                        ('code', '=', leave_type.name)])
                days_exclude += sum([work_days.number_of_days for work_days
                                     in worked_days_line_ids])
            result_days -= days_exclude
            if days_exclude != 0 or result_days < 30 and result_days > 0:
                if result_days > 30:
                    result_days = 30
                accum_month = (accum_month / 30) * result_days
            if result_days < 0 and accum_month > 0:
                accum_month = (accum_month / 30) * result_days
            accum_salary += accum_month
        result = accum_salary
        # Calculate before three months is the same salary Basic
        last_day_of_prev_month = date1.replace(
            day=1) + datetime.timedelta(days=-1)
        auxmonthbegin = 1
        if payslip.date_from.month > 3:
            auxmonthbegin = payslip.date_from.month - 3
        start_day_of_prev_month = date1.replace(month=(auxmonthbegin), day=1)
        payslips = self.env['hr.payslip'].search(
            [('date_from', '>=', start_day_of_prev_month),
             ('date_to', '<=', last_day_of_prev_month),
             ('employee_id', '=', self.id),
             ('state', 'in', ('done', 'paid'))])
        auxmonths = 0
        valmonthbefore = 0
        accum_month = 0
        for p_id in payslip_now:
            for line in p_id.ps_input_rf_ids:
                if line.rule_id.category_id.code in (list_categ):
                    accum_month += line.value_final
        result_days = sum([work_days.number_of_days for work_days
                           in payslip_now.worked_days_line_ids])
        for p_id in payslips:
            acc_salary = 0
            for line in p_id.line_ids:
                if line.salary_rule_id.category_id.code in (list_categ)\
                        and not\
                        line.slip_id.contract_id.exclude_from_seniority:
                    acc_salary += line.total
            if valmonthbefore == round(accum_month) and\
                acc_salary == valmonthbefore and\
                    result_days == 30:
                acc_salary = (acc_salary / 30) * \
                    self.get_days_annual(payslip.contract_id.date_end)
                result = acc_salary
            valmonthbefore = acc_salary
        return result

    @api.multi
    def get_average_paid_biannual(self, date, payslip, list_categ=(
            'BASIC', 'AUS', 'AUSINC', 'AUXTRANS', 'AJUSSAL', 'AUSAJUS')):
        """Function obtain summatory salary with basic category."""
        result = 0
        accum_salary = 0
        accum_month = 0
        add_month_actual = True
        if payslip.contract_id.father_contract_id:
            if payslip.contract_id.father_contract_id.date_end == date:
                add_month_actual = False
        date1 = fields.Date.from_string(date)
        payslip_now = self.env['hr.payslip'].search(
            [('id', '=', payslip.id)])
        result_days = sum([work_days.number_of_days for work_days
                           in payslip_now.worked_days_line_ids])
        if date1:
            if date1.month <= 6:
                last_day_of_prev_month = date1
                start_day_of_prev_month = date1.replace(month=1, day=1)
            else:
                last_day_of_prev_month = date1
                start_day_of_prev_month = date1.replace(month=7, day=1)
            payslips = self.env['hr.payslip'].search(
                [('date_from', '>=', start_day_of_prev_month),
                 ('date_to', '<=', last_day_of_prev_month),
                 ('employee_id', '=', self.id),
                 ('state', 'in', ('done', 'paid'))])
            for p_id in payslips:
                for line in p_id.line_ids:
                    if line.salary_rule_id.category_id.code in (list_categ)\
                            and not\
                            line.slip_id.contract_id.exclude_from_seniority:
                        accum_salary += line.total
            if add_month_actual:
                for p_id in payslip_now:
                    for line in p_id.ps_input_rf_ids:
                        if line.rule_id.category_id.code in (list_categ):
                            accum_month += line.value_final
            days_exclude = 0
            leaves_type_ids = self.env['hr.leave.type'].search([
                ('exclude_calculate_payslip', '=', True)])
            for leave_type in leaves_type_ids:
                worked_days_line_ids = self.env[
                    'hr.payslip.worked_days'].search([
                        ('payslip_id', '=', payslip.id),
                        ('code', '=', leave_type.name)])
                days_exclude += sum([work_days.number_of_days for work_days
                                     in worked_days_line_ids])
            result_days -= days_exclude
            if result_days > 30:
                result_days = 30
            accum_month = (accum_month / 30) * result_days
            accum_salary += accum_month
        result = accum_salary
        return result

    @api.multi
    def get_average_paid_quarterly(self, date, payslip, list_categ):
        """Function obtain summatory salary with basic category."""
        result = 0
        accum_salary = 0
        accum_month = 0
        date1 = fields.Date.from_string(date)
        payslip_now = self.env['hr.payslip'].search(
            [('id', '=', payslip.id)])
        result_days = sum([work_days.number_of_days for work_days
                           in payslip_now.worked_days_line_ids])
        if date1:
            if date1.month <= 3:
                last_day_of_prev_month = date1
                start_day_of_prev_month = date1.replace(month=1, day=1)
            else:
                last_day_of_prev_month = date1.replace(
                    day=calendar.monthrange(date1.year, date1.month)[1])
                start_day_of_prev_month = date1.replace(
                    month=date1.month - 2, day=1)
            payslips = self.env['hr.payslip'].search(
                [('date_from', '>=', start_day_of_prev_month),
                 ('date_to', '<=', last_day_of_prev_month),
                 ('employee_id', '=', self.id),
                 ('state', 'in', ('done', 'paid'))])
            for p_id in payslips:
                for line in p_id.line_ids:
                    if line.salary_rule_id.category_id.code in (list_categ):
                        accum_salary += line.total
            for p_id in payslip_now:
                for line in p_id.ps_input_rf_ids:
                    if line.rule_id.category_id.code in (list_categ):
                        accum_month += line.value_final
            accum_month = (accum_month / 30) * result_days
            accum_salary += accum_month
        result = accum_salary
        return result

    @api.multi
    def get_average_paid_quarterly_biannual(self, date, payslip, list_categ):
        """Function obtain summatory salary with basic category."""
        result = 0
        accum_salary = 0
        accum_month = 0
        date1 = fields.Date.from_string(date)
        payslip_now = self.env['hr.payslip'].search(
            [('id', '=', payslip.id)])
        result_days = sum([work_days.number_of_days for work_days
                           in payslip_now.worked_days_line_ids])
        if date1:
            if date1.month <= 3:
                last_day_of_prev_month = date1
                start_day_of_prev_month = date1.replace(month=1, day=1)
            elif date1.month in (7, 8):
                last_day_of_prev_month = date1
                start_day_of_prev_month = date1.replace(month=7, day=1)
            else:
                last_day_of_prev_month = date1.replace(
                    day=calendar.monthrange(date1.year, date1.month)[1])
                start_day_of_prev_month = date1.replace(
                    month=date1.month - 2, day=1)
            payslips = self.env['hr.payslip'].search(
                [('date_from', '>=', start_day_of_prev_month),
                 ('date_to', '<=', last_day_of_prev_month),
                 ('employee_id', '=', self.id),
                 ('state', 'in', ('done', 'paid'))])
            for p_id in payslips:
                for line in p_id.line_ids:
                    if line.salary_rule_id.category_id.code in (list_categ):
                        accum_salary += line.total
            for p_id in payslip_now:
                for line in p_id.ps_input_rf_ids:
                    if line.rule_id.category_id.code in (list_categ):
                        accum_month += line.value_final
            accum_month = (accum_month / 30) * result_days
            accum_salary += accum_month
        result = accum_salary
        return result

    @api.multi
    def day_week_friday(self, date):
        if date and date.strftime("%w") == '5':
            return True
        return False

    @api.multi
    def get_salary_leave(self, payslip, event, field='wage'):
        # Obtain contract for calculate values in leaves
        res = 0
        if payslip and event:
            type_leave_id = self.env['hr.leave.type'].search(
                [('name', '=', event)])
            if type_leave_id:
                leave_id = self.env['hr.leave'].search(
                    [('request_date_to', '>=', payslip.date_from),
                     ('request_date_from', '<', payslip.date_from),
                     ('employee_id', '=', payslip.employee_id),
                     ('holiday_status_id', '=', type_leave_id.id),
                     ('state', '=', 'validate')])
                if not leave_id:
                    leave_id = self.env['hr.leave'].search(
                        [('request_date_from', '<', payslip.date_to),
                         ('request_date_from', '>', payslip.date_from),
                         ('employee_id', '=', payslip.employee_id),
                         ('holiday_status_id', '=', type_leave_id.id),
                         ('state', '=', 'validate')])
                if leave_id:
                    contract_id = self.env['hr.contract'].search(
                        [('date_start', '<=', leave_id.request_date_from),
                         ('date_end', '>=', leave_id.request_date_from),
                         ('employee_id', '=', payslip.employee_id),
                         ('state', '=', 'close')])
                    if not contract_id:
                        contract_id = self.env['hr.contract'].search(
                            [('date_start', '<=', leave_id.request_date_from),
                             ('employee_id', '=', payslip.employee_id),
                             ('state', '=', 'open')])
                    if contract_id:
                        if field == 'fix_wage_amount':
                            res = contract_id.fix_wage_amount
                        elif field == 'flex_wage_amount':
                            res = contract_id.flex_wage_amount
                        else:
                            res = contract_id.wage
        return res
