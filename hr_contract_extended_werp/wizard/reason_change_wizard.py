# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import datetime

from odoo import models, api, fields, _


class ReasonChangeWizard(models.TransientModel):
    _name = "reason.change.wizard"
    _description = "Reason Change Wizard"

    reason_change_id = fields.Many2one(
        'hr.contract.reason.change', 'Reason Change', required=True)
    date_start = fields.Date()
    date_end = fields.Date()

    @api.model
    def default_get(self, lst_fields):
        """Fill Dates."""
        result = super(ReasonChangeWizard, self).default_get(lst_fields)
        contract_id = self.env[self._context.get('active_model', '')].browse(
            self._context.get('active_id', ''))
        if contract_id.date_end:
            if contract_id.date_end > fields.Date.today():
                result['date_end'] = contract_id.date_end
            else:
                result['date_start'] = contract_id.date_end +\
                    datetime.timedelta(days=1)
        return result

    @api.multi
    def create_subcontract(self):
        """Create Subcontract."""
        contract_id = self.env[self._context.get('active_model', '')].browse(
            self._context.get('active_id', ''))
        if contract_id:
            new_subcontract_id = contract_id.copy()
            new_subcontract_id.write({
                'subcontract': True, 'father_contract_id': contract_id.id,
                'date_start': self.date_start, 'date_end': self.date_end,
                'state': 'open'})
            contract_id.write({
                'state': 'close', 'subcontract': False,
                'reason_change_id': self.reason_change_id.id})
            if not contract_id.date_end:
                contract_id.write({
                    'date_end':
                    new_subcontract_id.date_start + datetime.timedelta(
                        days=-1)})
            if contract_id.date_end and\
                    contract_id.date_end > fields.Date.today():
                contract_id.write({
                    'date_end':
                    new_subcontract_id.date_start + datetime.timedelta(
                        days=-1)})
            if new_subcontract_id:
                return {
                    'name': _('Contracts'),
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'res_model': 'hr.contract',
                    'target': 'main',
                    'res_id': new_subcontract_id.id}
        return {'type': 'ir.actions.act_window_close'}
