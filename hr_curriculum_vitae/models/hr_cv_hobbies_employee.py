# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class HRCVHobbiesEmployee(models.Model):
    """This Class is used to define fields
    and methods for HR CV Hobbies Employee."""

    _name = "hr.cv.hobbies.employee"
    _description = "HR CV Hobbies Employee"

    hobby_id = fields.Many2one('hr.hobbies')
    employee_id = fields.Many2one('hr.employee')
    hr_cv_employee_id = fields.Many2one('hr.cv.employee')
    active = fields.Boolean(default=True)
    description = fields.Text()
