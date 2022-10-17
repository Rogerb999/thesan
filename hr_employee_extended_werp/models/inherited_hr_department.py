# Copyright 2020-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class HrDepartment(models.Model):
    """Overwrite the Hr Department."""

    _inherit = "hr.department"

    description = fields.Text()
