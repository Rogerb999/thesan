# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class FunctionExecuted(models.Model):
    """This Class is used to define fields and methods for Function Executed."""

    _name = "function.executed"
    _description = "Function Executed"

    name = fields.Char()
    description = fields.Text()
