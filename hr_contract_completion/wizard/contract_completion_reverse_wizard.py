# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ContractCompletionReverseWizard(models.TransientModel):
    _name = 'hr.contract.completion.reverse.wizard'
    _description = 'Contract Completion Reverse Wizard'

    reverse_reason = fields.Text(string="Reverse Reason")

    @api.multi
    def confirm(self):
        active_id = self.env.context.get('active_id')
        contract_completion_id = \
            self.env['hr.contract.completion'].browse(active_id)
        contract_completion_id.write({
            'reverse_reason': self.reverse_reason,
        })
