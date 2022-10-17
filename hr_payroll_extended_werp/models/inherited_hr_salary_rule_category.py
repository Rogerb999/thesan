# Copyright 2020-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class HrSalaryRuleCategory(models.Model):
    """Overwrite the Hr Salary Rule Category."""

    _inherit = "hr.salary.rule.category"

    active = fields.Boolean(default=True)
