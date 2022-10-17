# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, tools


class HRHolidays(models.Model):
    _inherit = 'hr.leave'

    public_holiday_id = fields.Many2one('hr.public_holiday', 'Public Holiday')


class HolidaysAllocation(models.Model):
    _inherit = 'hr.leave.allocation'

    public_holiday_id = fields.Many2one('hr.public_holiday', 'Public Holiday')
