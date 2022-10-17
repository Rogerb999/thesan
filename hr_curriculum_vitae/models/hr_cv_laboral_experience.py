# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class HRCVLaboralExperience(models.Model):
    """This Class is used to define fields
    and methods for HR CV Laboral Experience."""

    _name = "hr.cv.laboral.experience"
    _description = "HR CV Laboral Experience"

    company_id = fields.Many2one('res.partner')
    experience_area_id = fields.Many2one('hr.experience.area')
    start_date = fields.Date()
    end_date = fields.Date()
    ext_job_position_id = fields.Many2one('hr.external.job.position')
    position_range = fields.Selection([
        ('intern', 'Intern'),
        ('assistant', 'Assistant'),
        ('junior', 'Junior Professional'),
        ('senior', 'Senior Professional'),
        ('supervisor', 'Supervisor'),
        ('coordinator', 'Coordinator'),
        ('chief', 'Chief'),
        ('director', 'Director'),
        ('manager', 'Manager'),
        ('vice', 'Vice President'),
        ('president', 'President'),
    ])
    contract_type_id = fields.Many2one('hr.type.contract')
    function_summary = fields.Text()
    outstanding_achievements = fields.Text()
    hr_cv_employee_id = fields.Many2one('hr.cv.employee')
    employee_id = fields.Many2one('hr.employee')
    wage = fields.Float()
    country_id = fields.Many2one('res.country', string='Country')
    state_id = fields.Many2one(
        'res.country.state', 'State',
        domain="[('country_id', '=', country_id)]")
    city_id = fields.Many2one(
        'res.city', 'City', domain="[('state_id', '=', state_id)]")
    withdrawal_reason = fields.Char()
    active = fields.Boolean(default=True)
    description = fields.Text()
