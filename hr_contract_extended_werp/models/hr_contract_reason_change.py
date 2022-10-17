# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class HrContractReasonChange(models.Model):
    _name = 'hr.contract.reason.change'
    _description = 'Contract Reason Change'

    name = fields.Char('Name', required=True)
    description = fields.Text('Description')
