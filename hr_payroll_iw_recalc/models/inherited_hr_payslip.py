# Copyright 2020-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class HrPayslip(models.Model):
    """Hr Payslip."""

    _inherit = "hr.payslip"

    recalc_line_id = fields.Many2one('hr.recalc.lines')
    recalc = fields.Boolean(default=False)
