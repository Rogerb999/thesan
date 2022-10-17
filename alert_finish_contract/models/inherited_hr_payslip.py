# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from dateutil.relativedelta import relativedelta

from odoo import api, models, _
from odoo.exceptions import ValidationError


class HrPayslip(models.Model):
    """Overwrite the hr payslip."""

    _inherit = "hr.payslip"

    @api.onchange('employee_id', 'date_from', 'date_to')
    def onchange_employee(self):
        """Alert Check."""
        if self.date_to and self.struct_id and self.contract_id and\
                self.contract_id.date_start:
            alert = self.env['alert.finish.contract'].search([
                ('structure_id', '=', self.struct_id.id)])
            if alert:
                if alert.backup_type == 'start':
                    check_date = self.contract_id.date_start + relativedelta(
                        months=alert.periodicity)
                    if self.date_to >= check_date:
                        raise ValidationError(_(
                            'Alert Finish Contract Exceed.'))
                if alert.backup_type == 'end':
                    check_date = self.contract_id.date_start - relativedelta(
                        months=alert.periodicity)
        return super(HrPayslip, self).onchange_employee()
