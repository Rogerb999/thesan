# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class DaysCalculate(models.Model):
    """Days Calculate"""

    _name = "days.calculate"
    _description = 'Days Calculate'

    name = fields.Char('Name', required=True)
    year_from = fields.Integer('Year From', required=True)
    year_to = fields.Integer('Year To', required=True)
    quatity_days = fields.Integer('Quatity Days', required=True)
