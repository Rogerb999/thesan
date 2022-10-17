# -*- coding: utf-8 -*-

from odoo import api, fields, models


class NoveltyRejectWizard(models.TransientModel):
    _name = 'hr.novelty.reject.wizard'
    _description = 'Novelty Reject Wizard'

    reject_reason = fields.Text(string="Reject Reason")

    @api.multi
    def confirm(self):
        active_id = self.env.context.get('active_id')
        novelty_id = self.env['hr.novelty'].browse(active_id)
        novelty_id.write({
            'reject_reason': self.reject_reason,
            'state': 'rejected'})


class NoveltyCheckDateWizard(models.TransientModel):
    _name = 'hr.novelty.check.date.wizard'
    _description = 'Novelty Check Date'

    @api.multi
    def get_message(self):
        if self.env.context.get("message", False):
            return self.env.context.get("message")
        return False

    message = fields.Text(
        string="Message",
        readonly=True,
        default=get_message)
