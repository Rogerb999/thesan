# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class HREmployeesCV(models.Model):
    """This Class is used to define fields
    and methods for HR CV Employee."""

    _name = "hr.cv.employee"
    _description = "HR CV Employee"

    name = fields.Char('Name')
    employee_id = fields.Many2one('hr.employee')
    hobbies_ids = fields.One2many(
        'hr.cv.hobbies.employee', 'hr_cv_employee_id', 'Employee Hobbies')
    sport_ids = fields.One2many(
        'hr.cv.sports.employee', 'hr_cv_employee_id', 'Employee Sports')
    language_ids = fields.One2many(
        'hr.cv.language.employee', 'hr_cv_employee_id', 'Employee Languages')
    holding_ids = fields.One2many(
        'hr.cv.holding.employee', 'hr_cv_employee_id', 'Employee Holdings')
    family_group_ids = fields.One2many(
        'hr.cv.family.employee', 'hr_cv_employee_id', 'Employee Family Group')
    laboral_experience_ids = fields.One2many(
        'hr.cv.laboral.experience', 'hr_cv_employee_id', 'Laboral Experience')
    academic_studies_ids = fields.One2many(
        'hr.cv.academic.studies', 'hr_cv_employee_id', 'Academic Studies')
    animal_pets_ids = fields.One2many(
        'hr.cv.pets', 'hr_cv_employee_id', 'Animal Pets')
    personal_employee_ids = fields.One2many(
        'hr.cv.personal.employee', 'hr_cv_employee_id', 'Personal Employees')
    active = fields.Boolean(default=True)
    description = fields.Text()
