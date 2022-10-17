# -*- coding: utf-8 -*-
# Copyright 2020-TODAY WSuite Products <wsuite-products@wsuite.com`>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class HrEmployee(models.Model):
    """Adds Flex Time."""

    _inherit = "hr.employee"

    flex_id = fields.Many2one(
        'hr.employee.flextime', 'Flextime',
        track_visibility='onchange')
