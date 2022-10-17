# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import date
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models


class HRPetsCV(models.Model):
    """This Class is used to define fields
    and methods for HR CV Pets Employee."""

    _name = "hr.cv.pets"
    _description = "HR CV Pets Employee"

    name = fields.Char('Name')
    animal_type_id = fields.Many2one('animal.type', 'Type of Animal')
    animal_race_id = fields.Many2one('animal.race', 'Race')
    dob = fields.Date('Date of birth')
    age = fields.Char(compute='_compute_age', string='Age in Years')
    employee_id = fields.Many2one('hr.employee')
    hr_cv_employee_id = fields.Many2one('hr.cv.employee')
    active = fields.Boolean(default=True)
    description = fields.Text()

    @api.multi
    @api.depends('dob')
    def _compute_age(self):
        for rec in self:
            if rec.dob:
                rec.age = relativedelta(
                    fields.Date.today(), rec.dob).years
