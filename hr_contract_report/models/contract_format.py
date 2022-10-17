# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class ContractFormat(models.Model):
    _name = 'contract.format'
    _description = 'Contract Format'

    name = fields.Char('Name', required=True)
    report_id = fields.Many2one('ir.actions.report', 'Report')
    contract_section_ids = fields.One2many(
        'contract.section', 'contract_format_id', 'Contract Section Details')
