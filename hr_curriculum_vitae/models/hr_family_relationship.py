# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class HRFamilyRelationship(models.Model):
    """This Class is used to define fields
    and methods for HR Family Relationship."""

    _name = "hr.family.relationship"
    _description = "HR Family Relationship"

    name = fields.Char()
    description = fields.Text()
    hr_family_group_categ_id = fields.Many2one(
        'hr.family.group.categ', 'HR Family Group Category')
    active = fields.Boolean(default=True)
