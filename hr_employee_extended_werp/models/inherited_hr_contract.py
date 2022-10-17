# -*- coding: utf-8 -*-
# Copyright 2020-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class HrContract(models.Model):

    _inherit = "hr.contract"

    reference_arl_id = fields.Many2one('hr.arl')
    type_flex_id = fields.Many2one('hr.cotract.type')
