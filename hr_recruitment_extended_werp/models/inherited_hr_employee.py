# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class HrEmployee(models.Model):
    """Extends HR Employee."""

    _inherit = "hr.employee"

    macro_area_id = fields.Many2one(
        'macro.area', 'Macro Area', track_visibility='onchange')
    work_group_id = fields.Many2one('work.group', 'Work Group',
                                    track_visibility='onchange')
    function_executed_id = fields.Many2one(
        'function.executed', 'Function Executed',
        track_visibility='onchange')
