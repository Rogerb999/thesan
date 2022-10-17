# -*- coding: utf-8 -*-

from odoo import fields, models


class HrContract(models.Model):
    """Add reason in the contract."""

    _inherit = 'hr.contract'

    contract_completion_id = fields.Many2one('hr.contract.completion')
    hr_contract_completion_withdrawal_reason_id = fields.Many2one(
        'hr.contract.completion.withdrawal_reason',
        'Reason for Payroll Withdrawal')
    motivo_talento_id = fields.Many2one(
        'motivo.talento', 'Reason for Talent withdrawal')
