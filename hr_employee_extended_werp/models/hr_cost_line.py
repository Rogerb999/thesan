# -*- coding: utf-8 -*-
# Copyright 2020-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class HrCostLine(models.Model):
    """HrCostLine."""

    _name = 'hr.cost.line'
    _description = 'Hr Cost Line'

    name = fields.Char()
    name_interface = fields.Char()
    code = fields.Char()
    description = fields.Text()
