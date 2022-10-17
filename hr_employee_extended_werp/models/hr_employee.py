# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import odoo
from odoo import http
import logging
from odoo import models, fields, api, tools, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
import json

_logger = logging.getLogger(__name__)


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    last_update = fields.Date('Last Updated', track_visibility='onchange')
    update_info = fields.Boolean('Update Info?', track_visibility='onchange')
    address_id = fields.Many2one(
        'res.partner', 'Work Address', track_visibility='onchange')
    work_phone = fields.Char('Work Phone', track_visibility='onchange')
    mobile_phone = fields.Char('Work Mobile', track_visibility='onchange')
    work_email = fields.Char('Work Email', track_visibility='onchange')
    work_location = fields.Char('Work Location', track_visibility='onchange')
    job_id = fields.Many2one('hr.job', 'Job Position',
                             track_visibility='onchange')
    department_id = fields.Many2one(
        'hr.department', 'Department', track_visibility='onchange')
    parent_id = fields.Many2one(
        'hr.employee', 'Manager', track_visibility='onchange')
    coach_id = fields.Many2one(
        'hr.employee', 'Coach', track_visibility='onchange')
    manager = fields.Boolean(string='Is a Manager',
                             track_visibility='onchange')
    resource_calendar_id = fields.Many2one(
        'resource.calendar', 'Working Hours',
        default=lambda self: self.env[
            'res.company']._company_default_get().resource_calendar_id,
        index=True,
        related='resource_id.calendar_id', store=True,
        readonly=False, track_visibility='onchange')
    tz = fields.Selection(
        string='Timezone', related='resource_id.tz', readonly=False,
        help="This field is used in order to define in which "
        "timezone the resources will work.", track_visibility='onchange')
    country_id = fields.Many2one(
        'res.country', 'Nationality (Country)',
        groups="hr.group_hr_user", track_visibility='onchange')
    passport_id = fields.Char(
        'Passport No', groups="hr.group_hr_user", track_visibility='onchange')
    bank_account_id = fields.Many2one(
        'res.partner.bank', 'Bank Account Number',
        domain="[('partner_id', '=', address_home_id)]",
        groups="hr.group_hr_user",
        help='Employee bank salary account', track_visibility='onchange')
    address_home_id = fields.Many2one(
        'res.partner', 'Private Address',
        help='Enter here the private address of the employee, '
        'not the one linked to your company.',
        groups="hr.group_hr_user", track_visibility='onchange')
    emergency_contact = fields.Char(
        "Emergency Contact", groups="hr.group_hr_user",
        track_visibility='onchange')
    emergency_phone = fields.Char(
        "Emergency Phone", groups="hr.group_hr_user",
        track_visibility='onchange')
    km_home_work = fields.Integer(
        string="Km home-work", groups="hr.group_hr_user",
        track_visibility='onchange')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], groups="hr.group_hr_user", default="male", track_visibility='onchange')
    marital = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('cohabitant', 'Legal Cohabitant'),
        ('widower', 'Widower'),
        ('divorced', 'Divorced')
    ], string='Marital Status', groups="hr.group_hr_user",
        default='single', track_visibility='onchange')
    children = fields.Integer(
        string='Number of Children',
        groups="hr.group_hr_user", track_visibility='onchange')
    country_of_birth = fields.Many2one(
        'res.country', string="Country of Birth",
        groups="hr.group_hr_user", track_visibility='onchange')
    birthday = fields.Date(
        'Date of Birth', groups="hr.group_hr_user",
        track_visibility='onchange')
    permit_no = fields.Char(
        'Work Permit No', groups="hr.group_hr_user",
        track_visibility='onchange')
    visa_no = fields.Char(
        'Visa No', groups="hr.group_hr_user", track_visibility='onchange')
    visa_expire = fields.Date(
        'Visa Expire Date', groups="hr.group_hr_user",
        track_visibility='onchange')
    certificate = fields.Selection([
        ('bachelor', 'Bachelor'),
        ('master', 'Master'),
        ('other', 'Other'),
    ], 'Certificate Level', default='master', groups="hr.group_hr_user",
        track_visibility='onchange')
    study_field = fields.Char(
        "Field of Study", placeholder='Computer Science',
        groups="hr.group_hr_user", track_visibility='onchange')
    study_school = fields.Char(
        "School", groups="hr.group_hr_user", track_visibility='onchange')
    google_drive_link = fields.Char(
        string="Employee Documents",
        groups="hr.group_hr_user", track_visibility='onchange')
    additional_note = fields.Text(
        string='Additional Note', groups="hr.group_hr_user",
        track_visibility='onchange')
    Interface_salary_type = fields.Char()
    employment_relationship_id = fields.Many2one('hr.employment.relationship')
    code_office = fields.Char()
    salary_effective_date = fields.Date()
    unity_id = fields.Many2one('hr.employee.unity')
    zone_id = fields.Many2one('hr.employee.zone')
    cost_center_id = fields.Many2one('hr.cost.center')
    cost_line_id = fields.Many2one('hr.cost.line')
    functional_boss = fields.Char('Functional Boss')

    @api.model
    def default_get(self, fields):
        """Default timezone  America/Bogota."""
        rec = super(HrEmployee, self).default_get(fields)
        rec.update({'tz': 'America/Bogota'})
        return rec



    @api.multi
    def write(self, vals):
        if not vals.get('update_info'):
            vals.update({'last_update': fields.Date.today(),
                         'update_info': False
                         })
        active = vals.get('active')
        for rec in self:
            user = vals.get('user_id') or rec.user_id.id
            if active is False:
                if user or rec.user_id:
                    user_id = user or rec.user_id.id
                    self._cr.execute(
                        'UPDATE res_users SET active=%s WHERE id=%s',
                        (False, user_id))
                email = vals.get('work_email') or rec.work_email or False
            elif active is True:
                if user or rec.user_id:
                    user_id = user or rec.user_id.id
                    self._cr.execute(
                        'UPDATE res_users SET active=%s WHERE id=%s',
                        (True, user_id))
                email = vals.get('work_email') or rec.work_email or False
            if user is False or rec.user_id:
                if rec.user_id:
                    rec.user_id.employee_id = False
        res = super(HrEmployee, self).write(vals)
        for rec in self:
            if rec.user_id:
                rec.user_id.employee_id = rec.id
            else:
                res_user_id = self.env['res.users'].search([('login', '=', rec.work_email)])
                if res_user_id:
                    res_user_id.employee_id = False
        return res

    @api.model
    def create(self, vals):
        if not vals.get('update_info'):
            vals.update({'last_update': fields.Date.today(),
                         'update_info': False,
                         })
        return super(HrEmployee, self).create(vals)


    @api.onchange('address_home_id')
    def onchange_address_home_id(self):
        """Change name as per Private Address."""
        if self.address_home_id:
            self.name = self.address_home_id.name
