# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import date
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models


class HRCVFamilyGroupEmployee(models.Model):
    """This Class is used to define fields
    and methods for HR CV Family Group Employee."""

    _name = "hr.cv.family.employee"
    _description = "HR CV Family Group Employee"

    name = fields.Char('Name')
    family_rel_id = fields.Many2one(
        'hr.family.relationship', 'HR Family Relationship')
    same_home = fields.Boolean()
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ])
    birthdate = fields.Date('Date of birth')
    age = fields.Char(compute='_compute_age', string='Age in Years')
    occupation_id = fields.Many2one('hr.occupations')
    employee_id = fields.Many2one('hr.employee')
    hr_cv_employee_id = fields.Many2one('hr.cv.employee')
    contact_emergency = fields.Boolean()
    partner_id = fields.Many2one('res.partner', 'Partner')
    active = fields.Boolean(default=True)
    description = fields.Text()

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        self.name = False
        if self.partner_id:
            self.name = self.partner_id.name

    @api.multi
    @api.depends('birthdate')
    def _compute_age(self):
        for rec in self:
            if rec.birthdate:
                rec.age = relativedelta(
                    fields.Date.today(), rec.birthdate).years
