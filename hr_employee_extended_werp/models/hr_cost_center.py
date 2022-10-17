# -*- coding: utf-8 -*-
# Copyright 2020-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class HrCostCenter(models.Model):
    """HrCostCenter."""

    _name = 'hr.cost.center'
    _description = 'Hr Cost Center'

    name = fields.Char()
    name_interface = fields.Char()
    code = fields.Char()
    description = fields.Text()
