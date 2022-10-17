# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class HREmployees(models.Model):
    """This Class is used to define fields and methods for HR Employee."""

    _inherit = "hr.employee"
    _description = "HR Employee"

    hobbies_ids = fields.One2many(
        'hr.cv.hobbies.employee', 'employee_id', 'Employee Hobbies')
    sport_ids = fields.One2many(
        'hr.cv.sports.employee', 'employee_id', 'Employee Sports')
    language_ids = fields.One2many(
        'hr.cv.language.employee', 'employee_id', 'Employee Languages')
    holding_ids = fields.One2many(
        'hr.cv.holding.employee', 'employee_id', 'Employee Holdings')
    family_group_ids = fields.One2many(
        'hr.cv.family.employee', 'employee_id', 'Employee Family Group')
    laboral_experience_ids = fields.One2many(
        'hr.cv.laboral.experience', 'employee_id', 'Laboral Experience')
    academic_studies_ids = fields.One2many(
        'hr.cv.academic.studies', 'employee_id', 'Academic Studies')
    animal_pets_ids = fields.One2many(
        'hr.cv.pets', 'employee_id', 'Animal Pets')
    personal_employee_ids = fields.One2many(
        'hr.cv.personal.employee', 'employee_id', 'Personal Employees')
    academic_level_id = fields.Many2one('hr.academic.level')
