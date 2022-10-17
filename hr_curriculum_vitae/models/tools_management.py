# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ToolsManagment(models.Model):
    """This Class is used to define fields and methods for Tools Mmanagment."""

    _name = "tools.managment"
    _description = "Tools Managment"

    name = fields.Char()
    level = fields.Selection([
        ('low', 'Low'),
        ('intermediate', 'Intermediate'),
        ('high', 'High')])
