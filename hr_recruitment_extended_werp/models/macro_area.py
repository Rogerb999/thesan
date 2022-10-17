# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class MacroArea(models.Model):
    """This Class is used to define fields and methods for Macro Area."""

    _name = "macro.area"
    _description = "Macro Area"

    name = fields.Char()
    description = fields.Text()
    work_group_ids = fields.Many2many(
        'work.group', 'macro_area_work_group_default_rel',
        'macro_area_id', 'work_group_id', string='Work Groups')
