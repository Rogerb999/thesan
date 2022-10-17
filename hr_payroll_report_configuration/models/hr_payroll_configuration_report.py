# Copyright 2020-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class HrPayrollConfigurationReport(models.Model):
    """Hr Payroll Configuration Report."""

    _name = "hr.payroll.configuration.report"
    _description = "Hr Payroll Configuration Report"

    name = fields.Char()
    code = fields.Char()
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("done", "Done"),
            ("expired", "Expired"),
        ], default="draft")
    hr_items_lines_ids = fields.Many2many(
        'hr.items.lines',
        'hr_payroll_configuration_report_hr_items_lines_default_rel',
        'hr_payroll_configuration_report_id', 'hr_items_lines_id',
        string="Items")

    def move_done(self):
        """Move to Done."""
        for rec in self:
            rec.state = 'done'

    def move_expired(self):
        """Move to Expired."""
        for rec in self:
            rec.state = 'expired'

    def move_draft(self):
        """Move to Draft."""
        for rec in self:
            rec.state = 'draft'
