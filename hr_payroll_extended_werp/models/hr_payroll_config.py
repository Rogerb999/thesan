# Copyright 2020-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HrPayrollConfig(models.Model):
    """Hr Payroll Config."""

    _name = "hr.payroll.config"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    name = fields.Char(track_visibility='always')
    start_date = fields.Date(track_visibility='always')
    end_date = fields.Date(track_visibility='always')
    config_line_ids = fields.One2many(
        'hr.payroll.config.lines', 'hr_payroll_config_id')
    state = fields.Selection(
        [("draft", "Draft"),
         ("done", "Done"),
         ("reject", "Reject")], default="draft", track_visibility='always',
        copy=False)
    reason_reject = fields.Char(track_visibility='always', copy=False)

    @api.constrains('start_date', 'end_date')
    def date_validation(self):
        """Start date must be less than End Date."""
        if self.start_date > self.end_date:
            raise ValidationError("Start date must be less than End Date")

    @api.multi
    def move_to_done(self):
        """Move to Done."""
        for rec in self:
            rec.state = 'done'

    @api.multi
    def move_to_draft(self):
        """Move to Draft."""
        for rec in self:
            rec.state = 'draft'

    @api.multi
    def move_to_reject(self):
        """Move to Reject."""
        return {
            'name': _('Reason Reject'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'payroll.config.reason.reject',
            'view_id': self.env.ref(
                'hr_payroll_extended_werp.payroll_config_reason_reject_form').id,
            'target': 'new',
        }

    @api.multi
    def unlink(self):
        """You cannot delete Done record."""
        for item in self:
            if item.state == 'done':
                raise ValidationError(_(
                    "You cannot delete Done record!"))
        return super(HrPayrollConfig, self).unlink()


class HrPayrollConfigLines(models.Model):
    """Hr Payroll Config Lines."""

    _name = "hr.payroll.config.lines"
    _description = "Hr Payroll Config Lines"

    variable = fields.Many2one(
        'hr.payroll.config.parameters', ondelete='restrict')
    name = fields.Char(related="variable.name", store="True")
    value = fields.Float()
    hr_payroll_config_id = fields.Many2one('hr.payroll.config')
