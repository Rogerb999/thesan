# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HrNovelty(models.Model):
    """Hr Novelties."""
    _inherit = 'hr.novelty'

    deduction_employee_id = fields.Many2one(
        'hr.deductions.rf.employee', string="Deduction",
        track_visibility='onchange')

    @api.multi
    def create_withholding(self):
        if self.event_id.deduction_id:
            wi_id = self.env['hr.deductions.rf.employee'].create({
                'name': self.event_id.deduction_id.name,
                'hr_deduction_type_id': self.event_id.deduction_id.type_id.id,
                'hr_deduction_id': self.event_id.deduction_id.id,
                'value': self.amount,
                'employee_id': self.employee_id.id,
                'active': True,
                'start_date': self.start_date,
                'end_date': self.end_date,
            })
            self.write({'deduction_employee_id': wi_id.id})
        else:
            raise ValidationError(_(
                'Please configure value in event for withholding income.'))
        return True

    @api.multi
    def action_approve(self):
        res = super(HrNovelty, self).action_approve()
        if self.event_id.income_withholding:
            self.create_withholding()
        return res


class HrNoveltyEvent(models.Model):
    """Hr Novelties event."""
    _inherit = 'hr.novelty.event'

    income_withholding = fields.Boolean(string='Income Withholding',
                                        track_visibility='onchange')
    deduction_id = fields.Many2one(
        'hr.deduction.rf', string="Deduction",
        track_visibility='onchange')
