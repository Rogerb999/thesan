# Copyright 2020-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class HrGroupRules(models.Model):
    """Hr Group Rules."""

    _name = "hr.group.rules"
    _description = "Hr Group Rules"

    name = fields.Char()
    code = fields.Char()
    salary_rules_ids = fields.Many2many(
        'hr.salary.rule',
        'hr_group_rules_hr_salary_rule_default_rel',
        'hr_group_rules_id', 'hr_salary_rule_id')
