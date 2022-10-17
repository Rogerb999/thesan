# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class ResUsers(models.Model):
    _inherit = 'res.users'

    employee_id = fields.Many2one(
        'hr.employee', string='Related Employee', ondelete='restrict')
