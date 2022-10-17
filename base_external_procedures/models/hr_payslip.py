# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


class HRPayslip(models.Model):

    _inherit = "hr.payslip"

    @api.multi
    def action_execute(self):
        try:
            self.compute_sheet()
        except:
            model_id = self.env['ir.model'].search([('model', '=', 'hr.payslip')])
            self.env['res.external.procedures'].create({
                'model_id': model_id and model_id.id,
                'function': 'compute_sheet',
                'model_ids': self.ids,
                'state': 'draft'
                })


class HRPayslip(models.Model):

    _inherit = "hr.payslip.run"

    @api.multi
    def action_execute(self):
        try:
            self.compute_sheet()
        except:
            model_id = self.env['ir.model'].search([('model', '=', 'hr.payslip')])
            self.env['res.external.procedures'].create({
                'model_id': model_id and model_id.id,
                'function': 'compute_sheet',
                'model_ids': self.slip_ids.ids,
                'state': 'draft'
                })