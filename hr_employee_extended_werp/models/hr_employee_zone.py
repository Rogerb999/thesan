# -*- coding: utf-8 -*-
# Copyright 2020-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class HrEmployeeZone(models.Model):
    """HrEmployeeZone."""

    _name = 'hr.employee.zone'
    _description = 'Hr Employee Zone'

    name = fields.Char()
    code = fields.Char()
    description = fields.Text()
