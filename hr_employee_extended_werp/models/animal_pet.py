# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import date
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models


class AnimalPet(models.Model):
    """This Class is used to define fields
    and methods for Animal Pet."""

    _name = "animal.pet"
    _description = "Animal Pet"

    name = fields.Char('Name')
    animal_type_id = fields.Many2one('animal.type', 'Animal Type')
    animal_race_id = fields.Many2one('animal.race', 'Animal Race')
    dob = fields.Date('Date of birth')
    age = fields.Char(compute='_compute_age', string='Age in Years')

    @api.multi
    @api.depends('dob')
    def _compute_age(self):
        for rec in self:
            if rec.dob:
                rec.age = relativedelta(fields.Date.today(), rec.dob).years
