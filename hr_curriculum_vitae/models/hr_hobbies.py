# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class HRHobbies(models.Model):
    """This Class is used to define fields and methods for HR Hobbies."""

    _name = "hr.hobbies"
    _description = "HR Hobbies"

    name = fields.Char()
    hobby_categ_id = fields.Many2one('hr.category.hobbies', 'Hobby Category')
    active = fields.Boolean(default=True)
