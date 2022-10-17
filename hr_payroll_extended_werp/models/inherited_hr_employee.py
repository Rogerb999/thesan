# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from pytz import utc
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from datetime import datetime
from odoo import fields, models, api
from odoo.tools.float_utils import float_round


class HrEmployee(models.Model):
    """Hr Employee."""

    _inherit = "hr.employee"

    hr_employee_acumulate_ids = fields.One2many(
        'hr.employee.acumulate', 'employee_id')
    allocation_leaves_count = fields.Float(
        'Allocation Leaves', track_visibility='onchange')
    leave_days_count = fields.Float(
        'Taken Leaves', track_visibility='onchange')
    remaining_leaves_count = fields.Float(
        'Remaining Leaves', track_visibility='onchange')
    compensation_company_id = fields.Many2one(
        'res.company', 'Compensation Company',
        default=lambda self: self.env.user.company_id)

    def list_leaves_payroll(
            self, from_datetime, to_datetime, calendar=None, domain=None):
        """
            By default the resource calendar is used, but it can be
            changed using the `calendar` argument.

            `domain` is used in order to recognise the leaves to take,
            None means default value ('time_type', '=', 'leave')

            Returns a list of tuples (day, hours, resource.calendar.leaves)
            for each leave in the calendar.
        """
        resource = self.resource_id
        calendar = calendar or self.resource_calendar_id

        # naive datetimes are made explicit in UTC
        if not from_datetime.tzinfo:
            from_datetime = from_datetime.replace(
                tzinfo=utc)
        if not to_datetime.tzinfo:
            to_datetime = to_datetime.replace(
                tzinfo=utc)
        attendances = calendar._attendance_intervals(
            from_datetime, to_datetime, resource)
        leaves = calendar._leave_intervals_payroll(
            from_datetime, to_datetime, resource, domain)
        result = []
        for start, stop, leave in (leaves & attendances):
            hours = (stop - start).total_seconds() / 3600
            result.append((start.date(), hours, leave))
        return result

    @api.multi
    def calculate_leaves_details(self):
        domain = [
            ('employee_id', 'in', self.ids),
            ('holiday_status_id.allocation_type', '!=', 'no'),
            ('holiday_status_id.autocalculate_leave', '=', True),
            ('state', '=', 'validate')
        ]
        leave_not_count = 0.0
        contract_comp = self.env['hr.contract.completion'].search([
            ('employee_id', '=', self.id)], limit=1)
        if contract_comp:
            for leave in self.env['hr.leave'].search(
                    [('employee_id', '=', self.id),
                     ('holiday_status_id.name', '=', 'Vacaciones'),
                     ('request_date_to', '>', contract_comp.date)]):
                leave_not_count += leave.number_of_days_display
        fields = ['number_of_days', 'employee_id']
        all_allocations = self.env['hr.leave.allocation'].read_group(
            domain, fields, groupby=['employee_id'])
        all_leaves = self.env['hr.leave.report'].read_group(
            domain, fields, groupby=['employee_id'])

        mapping_allocation = dict([(
            allocation['employee_id'][0], allocation['number_of_days']
        ) for allocation in all_allocations])
        mapping_leave = dict([(
            leave['employee_id'][0],
            leave['number_of_days']) for leave in all_leaves])

        for employee in self:
            allocation_leaves_count = float_round(
                mapping_allocation.get(employee.id, 0), precision_digits=2)
            remaining_leaves_count = float_round(
                mapping_leave.get(employee.id, 0), precision_digits=2)
            self._cr.execute('UPDATE hr_employee SET '
                             'allocation_leaves_count=%s, '
                             'remaining_leaves_count=%s, '
                             'leave_days_count=%s WHERE id=%s',
                             (allocation_leaves_count, remaining_leaves_count,
                              allocation_leaves_count -
                              remaining_leaves_count - leave_not_count,
                              employee.id))
            # employee.write({
            #     'allocation_leaves_count': allocation_leaves_count,
            #     'remaining_leaves_count': remaining_leaves_count,
            #     'leave_days_count': allocation_leaves_count -
            # remaining_leaves_count
            # })

    @api.multi
    def obtain_value(self, parameter, date):
        """Function to fetch Config of the salary rule."""
        result = 0
        payroll_config_id = self.env['hr.payroll.config'].search(
            [('start_date', '<=', date),
             ('end_date', '>=', date),
             ('state', '=', 'done')])
        for config in payroll_config_id:
            for config_line in config.config_line_ids:
                if config_line.name == parameter:
                    result += config_line.value
        return result
