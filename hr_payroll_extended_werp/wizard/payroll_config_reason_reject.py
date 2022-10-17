# Copyright 2020-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class PayrollConfigReasonReject(models.TransientModel):
    _name = 'payroll.config.reason.reject'
    _description = 'Payroll Config Reason Reject'

    reason_reject = fields.Char()

    @api.multi
    def confirm(self):
        """Reject Payroll Config."""
        active_id = self.env.context.get('active_id')
        payroll_config_id = self.env['hr.payroll.config'].browse(active_id)
        payroll_config_id.write({
            'reason_reject': self.reason_reject,
            'state': 'reject'})
