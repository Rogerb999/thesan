# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class HrLeaveCode(models.Model):
    """Hr Leave Code."""

    _name = 'hr.leave.code'
    _description = 'Hr Leave Code'

    name = fields.Char()
    code = fields.Char()
