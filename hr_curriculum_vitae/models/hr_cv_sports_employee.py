# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class HRCVSportsEmployee(models.Model):
    """This Class is used to define fields
    and methods for HR CV Sports Employee."""

    _name = "hr.cv.sports.employee"
    _description = "HR CV Sports Employee"
    _rec_name = 'sport_id'

    sport_id = fields.Many2one('hr.sports')
    employee_id = fields.Many2one('hr.employee')
    hr_cv_employee_id = fields.Many2one('hr.cv.employee')
    active = fields.Boolean(default=True)
    description = fields.Text()
