# -*- coding: utf-8 -*-
# Copyright 2020-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class HrArl(models.Model):
    """HrArl."""

    _name = 'hr.arl'
    _description = 'Hr Arl'

    @api.depends('level', 'level.name', 'percentage')
    def _compute_name(self):
        for rec in self:
            if rec.level and rec.level.name and rec.percentage:
                rec.name = rec.level.name + ' ' + str(round(rec.percentage, 2))

    name = fields.Char(compute='_compute_name')
    level = fields.Many2one('hr.arl.level')
    percentage = fields.Float()
    description = fields.Text()
