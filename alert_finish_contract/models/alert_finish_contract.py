# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


class AlertFinishContract(models.Model):
    """Add Alert Finish Contract."""

    _name = "alert.finish.contract"
    _rec_name = "backup_type"
    _description = "Alert Finish Contract"

    @api.multi
    @api.depends('periodicity')
    def _compute_month(self):
        for rec in self:
            if rec.periodicity:
                if rec.periodicity >= 1.0 and rec.periodicity <= 1.9:
                    rec.month = 'January'
                if rec.periodicity >= 2.0 and rec.periodicity <= 2.9:
                    rec.month = 'February'
                if rec.periodicity >= 3.0 and rec.periodicity <= 3.9:
                    rec.month = 'March'
                if rec.periodicity >= 4.0 and rec.periodicity <= 4.9:
                    rec.month = 'April'
                if rec.periodicity >= 5.0 and rec.periodicity <= 5.9:
                    rec.month = 'May'
                if rec.periodicity >= 6.0 and rec.periodicity <= 6.9:
                    rec.month = 'June'
                if rec.periodicity >= 7.0 and rec.periodicity <= 7.9:
                    rec.month = 'July'
                if rec.periodicity >= 8.0 and rec.periodicity <= 8.9:
                    rec.month = 'August'
                if rec.periodicity >= 9.0 and rec.periodicity <= 9.9:
                    rec.month = 'September'
                if rec.periodicity >= 10.0 and rec.periodicity <= 10.9:
                    rec.month = 'October'
                if rec.periodicity >= 11.0 and rec.periodicity <= 11.9:
                    rec.month = 'November'
                if rec.periodicity >= 12.0 and rec.periodicity <= 12.9:
                    rec.month = 'December'

    backup_type = fields.Selection([
        ('start', 'Start'),
        ('end', 'End')], default='start')
    periodicity = fields.Float()
    month = fields.Char(compute="_compute_month")
    structure_id = fields.Many2one('hr.payroll.structure', 'Payroll Structure')
