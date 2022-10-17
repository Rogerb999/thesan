# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class WorkGroup(models.Model):
    """This Class is used to define fields and methods for Work Group."""

    _name = "work.group"
    _description = "Work Group"

    name = fields.Char()
    description = fields.Text()
    function_executed_ids = fields.Many2many(
        'function.executed', 'work_group_function_executed_default_rel',
        'work_group_id', 'function_executed_id', string='Function Executed')
