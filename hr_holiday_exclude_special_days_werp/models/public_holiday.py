# -*- coding: utf-8 -*-
# © 2017 Jérôme Guerriat, Tobias Zehntner
# © 2017 Niboo SPRL (<https://www.niboo.be/>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import datetime
from odoo import api, exceptions, fields, models
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.exceptions import ValidationError


class PublicHoliday(models.Model):
    _name = 'hr.public_holiday'

    date = fields.Date('Public Holiday Date', required=True)
    name = fields.Char(string='Holiday Name', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
    ], default='draft')

    company_ids = fields.Many2many('res.company', string='Companies')
    tag_ids = fields.Many2many('hr.employee.category', string='Tags')
    employee_ids = fields.Many2many('hr.employee', string='Impacted Employees',
                                    required=True)
    holiday_status_id = fields.Many2one(
        'hr.leave.type', 'Leave Type', required=True,
        default=lambda self: self.get_default_holiday_status())
    allocation_leave = fields.Boolean(string='Create Allocation Leave?', default=True)

    def get_default_holiday_status(self):
        public_holidays = self.env['hr.leave.type'].search([
            ('is_public_holiday', '=', True)])
        if public_holidays:
            return public_holidays[0].id

    @api.onchange('company_ids', 'tag_ids')
    def _onchange_function(self):
        domain = []
        if self.company_ids:
            domain.append(('company_id', 'in', self.company_ids.ids))

        if self.tag_ids:
            domain.append(('category_ids', 'in', self.tag_ids.ids))

        if domain:
            employees = self.env['hr.employee'].search(domain)

            self.employee_ids = employees.ids
        else:
            self.employee_ids = False

    @api.multi
    def create_leaves(self):
        """
        This method will create a leave for all selected employees
        """
        self.ensure_one()
        if self.state != 'draft':
            raise exceptions.ValidationError('You can only create a leave '
                                             'from a public holiday in state '
                                             '"draft"')

        self.create_employee_leaves(self.employee_ids)
        self.state = 'done'

    @api.multi
    def create_employee_leaves(self, employee_ids):
        """
        This method will create a leave for the employees passed in parameter
        :param employee_ids: the employees to create the leave for
        """
        self.ensure_one()
        if not self.holiday_status_id:
            raise exceptions.ValidationError(
                'No Leave Type has been configured as Public Holiday. Please '
                'go to Configuration > Leave Types and tick the box \'Public '
                'Holiday\' on the desired leave type.')
        HRHolidays = self.env['hr.leave']
        HrLeaveAllocation = self.env['hr.leave.allocation']
        date_from, date_to = self.compensate_user_tz(self.date)
        values = {
            'name': self.name,
            'holiday_type': 'employee',
            'holiday_status_id': self.holiday_status_id.id,
            'date_from': date_from,
            'date_to': date_to,
            'number_of_days': 1,
            'state': 'confirm',
            'public_holiday_id': self.id,
        }
        context = {
            'mail_create_nosubscribe': True,
            'mail_create_nolog': True,
            'mail_notrack': True,
            'tracking_disable': True
        }

        # add the employee in case we generate for newcomers
        self.employee_ids += employee_ids

        allocation_vals = {
            'unit_per_interval': 'hours',
            'name': self.holiday_status_id.name,
            'interval_unit': 'weeks',
            'number_of_days_display': 1,
            'number_of_days': 1,
            'holiday_type': 'employee',
            'holiday_status_id': self.holiday_status_id.id,
            'interval_number': 1,
            'number_per_interval': 1,
            'state': 'confirm',
            'public_holiday_id': self.id,
        }
    
        for employee in employee_ids:
            values['employee_id'] = employee.id
            try:
                if self.allocation_leave:
                    allocation_vals['employee_id'] = employee.id
                    allocation = HrLeaveAllocation.sudo().with_context(context).create(values)
                    allocation.with_context(context).action_approve()
                leave = HRHolidays.sudo().with_context(context).create(values)
                leave.with_context(context).action_validate()
            except ValidationError as e:
                raise exceptions.ValidationError(
                    'The leave entries could not be generated as the '
                    'following error occurred:\n\n%s: %s'
                    % (employee.name, e.name))

    @api.multi
    def remove_leaves(self):
        """
        This method will remove the leave and its related
        analytic entries for all impacted employees
        """
        self.ensure_one()

        if self.state != 'done':
            raise exceptions.ValidationError('You can only delete a leave '
                                             'from a public holiday in state '
                                             '"done"')
        if self.env.user.has_group('base.group_system') \
                or self.env.user.has_group('hr.group_hr_manager'):
            hr_leave_ids = self.env['hr.leave'].search([('public_holiday_id', '=', self.id)])
            hr_leave_allocation_ids = self.env['hr.leave.allocation'].search([('public_holiday_id', '=', self.id)])
            hr_leave_ids.sudo().write({'state': 'draft'})
            hr_leave_ids.sudo().unlink()
            hr_leave_allocation_ids.sudo().write({'state': 'draft'})
            hr_leave_allocation_ids.sudo().unlink()
            resource_calendar_leaves_ids = self.env['resource.calendar.leaves'].search([('name', '=', self.name)])
            resource_calendar_leaves_ids.unlink()
        else:
            raise exceptions.ValidationError(
                'You do not have the rights to delete leave entries')
        self.state = 'draft'

    def compensate_user_tz(self, date):
        '''
        Return date compensated from user timezone
        :param date:
        :return:
        '''
        if not self.env.user.tz:
            raise exceptions.ValidationError('Please set a timezone in your '
                                             'user settings to assure a '
                                             'correct generation of leave '
                                             'entries.')
        date_obj = datetime.strptime(str(date), DF)
        date_from = datetime.combine(date_obj, datetime.min.time())
        date_to = datetime.combine(date_obj, datetime.max.time())
        user_tz_offset = \
            fields.Datetime.context_timestamp(
                self.sudo(self._uid), date_from).tzinfo._utcoffset
        date_from_tz_comp = date_from - user_tz_offset
        date_to_tz_comp = date_to - user_tz_offset
        date_from_tz_comp_str = date_from_tz_comp.strftime(DTF)
        date_to_tz_comp_str = date_to_tz_comp.strftime(DTF)

        return date_from_tz_comp_str, date_to_tz_comp_str

    @api.multi
    def open_generate_wizard(self):
        """
        Open wizard to generate leave entry for newcomers
        """
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hr_holiday.generate_holiday_wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
        }


class HRHolidaysStatus(models.Model):
    _inherit = 'hr.leave.type'

    is_public_holiday = fields.Boolean('Public Holiday')
