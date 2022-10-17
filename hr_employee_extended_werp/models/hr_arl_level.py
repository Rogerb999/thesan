# -*- coding: utf-8 -*-
# Copyright 2020-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class HrArlLevel(models.Model):
    """HrArlLevel."""

    _name = 'hr.arl.level'
    _description = 'Hr Arl Level'

    name = fields.Char()
    code = fields.Char()
    description = fields.Text()
