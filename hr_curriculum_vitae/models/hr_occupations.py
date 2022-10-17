# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class HROccupations(models.Model):
    """This Class is used to define fields and methods for HR Occupations."""

    _name = "hr.occupations"
    _description = "HR Occupations"

    name = fields.Char()
    description = fields.Text()
    active = fields.Boolean(default=True)
