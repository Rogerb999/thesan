# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class HRSports(models.Model):
    """This Class is used to define fields and methods for HR Sports."""

    _name = "hr.sports"
    _description = "HR Sports"

    name = fields.Char()
    description = fields.Text()
    active = fields.Boolean(default=True)
