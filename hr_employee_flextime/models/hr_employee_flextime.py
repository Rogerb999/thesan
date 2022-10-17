# Copyright 2020-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class HrEmployeeFlextime(models.Model):
    """Employee Flex Time."""

    _name = "hr.employee.flextime"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.depends('hour_start', 'hour_start_type', 'hour_end', 'hour_end_type')
    def _calculate_name(self):
        for rec in self:
            if rec.hour_start and rec.hour_start_type and\
                    rec.hour_end and rec.hour_end_type:
                rec.name = '{0:01.0f}:{1:02.0f} '.format(*divmod(float(
                    rec.hour_start) * 60, 60)) + str(
                        rec.hour_start_type) +\
                    ' - {0:01.0f}:{1:02.0f} '.format(
                        *divmod(float(rec.hour_end) * 60, 60)) + str(
                            rec.hour_end_type)

    name = fields.Char(compute='_calculate_name', track_visibility='onchange')
    hour_start = fields.Float(track_visibility='onchange')
    hour_start_type = fields.Selection([
        ('am', 'am'),
        ('pm', 'pm')], default='am', track_visibility='onchange')
    hour_end = fields.Float(track_visibility='onchange')
    hour_end_type = fields.Selection([
        ('am', 'am'),
        ('pm', 'pm')], default='pm', track_visibility='onchange')
    description = fields.Text(track_visibility='onchange')
