# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class HrNovelty(models.Model):
    _inherit = 'hr.novelty'

    motivo_nomina_id = fields.Many2one(
        'hr.contract.completion.withdrawal_reason', 'Motivo Nomina',
        track_visibility='onchange')
    reason_talent_id = fields.Many2one(
        'hr.contract.completion.withdrawal_reason', 'Motivo Nomina',
        track_visibility='onchange')
    contract_terminated_id = fields.Many2one(
        'hr.contract.completion', 'Contract Completion',
        track_visibility='onchange')

    @api.multi
    def _create_record(self):
        if self.subtype_id == self.env.ref(
                'hr_novelty.novelty_subtype_TERM_CONTR'):
            message = self.create_contract_completion()
            self.message_post(
                body=message,
                partner_ids=self.message_follower_ids)
        return super(HrNovelty, self)._create_record()

    @api.multi
    def create_contract_completion(self):
        contract = self.env['hr.contract.completion'].create({
            'employee_id': self.employee_id.id,
            'date': self.start_date.replace(hour=0, minute=00),
            'unjustified': self.event_id.unjustified,
            'transfer_employee': self.event_id.transfer_employee,
            'state': 'draft',
            'novelty_id': self.id
        })
        self.contract_terminated_id = contract.id
        return _("A new Contract Completion has been created")
