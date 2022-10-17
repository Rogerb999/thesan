# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class ContractSection(models.Model):
    _name = 'contract.section'
    _description = 'Contract Section'

    name = fields.Char('Name', required=True)
    description = fields.Html('Description')
    sequence = fields.Integer(help="Gives the sequence of this line when "
                                   "displaying the contract section.")
    contract_format_id = fields.Many2one('contract.format', 'Contract Format')
