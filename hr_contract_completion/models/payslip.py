# -*- coding: utf-8 -*-

from odoo import api, fields, models


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    contract_completion_id = fields.Many2one('hr.contract.completion')

    '''
    @api.model
    def create(self, vals):
        res = super(HrPayslip, self).create(vals)
        contract = res.get_contract(
            res.employee_id, res.date_from, res.date_to)
        if contract:
            contract_id = self.env['hr.contract'].browse(contract[0])
            nonvelty = self.env['hr.novelty'].search([
                ('contract_terminated_id', '=', res.contract_completion_id.id),
            ])
            if nonvelty:
                contract_id.write({
                    'hr_contract_completion_withdrawal_reason_id':
                    nonvelty.reason_talent_id.id,
                    'motivo_talento_id': nonvelty.motivo_talento_id.id})
        return res
    '''

    @api.multi
    def action_payslip_done(self):
        res = super(HrPayslip, self).action_payslip_done()
        if self.contract_completion_id:
            self.contract_completion_id.state = 'paid'
        hr_novelty_rec = self.env['hr.novelty'].search(
            [('start_date', '>=', self.date_from),
             ('start_date', '<=', self.date_to),
             ('state', 'in', ['wait', 'wait_comments']),
             ('employee_id', '=', self.employee_id.id),
             ('subtype_id', '!=', self.env.ref(
                 'hr_novelty.novelty_subtype_FIJ').id)])
        for novelty in hr_novelty_rec:
            if novelty.check_approver():
                novelty.action_approve()
        hr_novelty_rec = self.env['hr.novelty'].search(
            [('start_date', '>=', self.date_from),
             ('start_date', '<=', self.date_to),
             ('state', '=', 'approved'),
             ('employee_id', '=', self.employee_id.id),
             # ('is_user_appr', '!=', False),
             ('subtype_id', '!=', self.env.ref(
                 'hr_novelty.novelty_subtype_FIJ').id)])
        for novelty in hr_novelty_rec:
            novelty.action_process()
        return res

    @api.onchange('contract_id')
    def onchange_contract(self):
        super(HrPayslip, self).onchange_contract()
        self.journal_id = self.env['account.journal'].search(
            [('name', 'like', '%NOMINA%')], limit=1).id
