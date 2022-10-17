# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class HrLeavesGenerate(models.Model):
    """Added Hr Leaves Generate."""

    _name = "hr.leaves.generate"
    _description = "Hr Leaves Generate"
    _rec_name = "leave_id"

    leave_id = fields.Many2one(
        'hr.leave.type', 'Leave Type')
    days = fields.Float()
