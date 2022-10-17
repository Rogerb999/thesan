# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class HRCVPersonalReferenceEmployee(models.Model):
    """This Class is used to define fields
    and methods for HR CV Personal Reference Employee."""

    _name = "hr.cv.personal.employee"
    _description = "HR CV Personal Reference Employee"

    name = fields.Char('Name')
    partner_id = fields.Many2one('res.partner')
    occupation_id = fields.Many2one('hr.occupations', 'Occupation')
    occupation_name = fields.Char("Occupation")
    employee_id = fields.Many2one('hr.employee')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ])
    type_id = fields.Many2one('hr.cv.personal.employee.type', 'Type')
    hr_cv_employee_id = fields.Many2one('hr.cv.employee')
    active = fields.Boolean(default=True)
    description = fields.Text()
