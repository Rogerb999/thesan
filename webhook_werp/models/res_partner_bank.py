# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api, fields, _
import json
import logging
import threading
from datetime import date, datetime
_logger = logging.getLogger(__name__)


class ResPartnerBank(models.Model):
    _inherit = "res.partner.bank"

    @api.multi
    def write(self, vals):
        if vals.get('bank_id', False) or vals.get('acc_number', False) or vals.get('acc_holder_name', False) or vals.get('type', False):
            self.action_webhook_werp_update_partner_bank_data(22, vals)
        res = super(ResPartnerBank, self).write(vals)
        return res

    @api.multi
    def get_generic_details(self, webhook_werp_type, vals):
        final_data = {
            'from': {},
            'to': {},
            'data': {},
            'webhook_werp_type': webhook_werp_type,
            'webhook_werp_history_id': {},
            'reference': '%s,%s' % (self._name, self.id)
        }
        read_data = self.read(vals.keys())[0]
        return final_data, read_data

    @api.multi
    def action_webhook_werp_update_partner_bank_data(self, webhook_werp_type, vals):
        webhook_werp_ids = self.env['webhook_werp'].search(
            [('model_id.model', '=', 'res.partner.bank'),
             ('url_type', '=', 'w_plan'),
             ('trigger', 'in', ['on_create', 'on_write', 'on_create_or_write'])])
        for webhook_werp_id in webhook_werp_ids:
            if vals:
                final_data, read_data = self.get_generic_details(
                    webhook_werp_type, vals)
            employee_id = self.env['hr.employee'].search([('bank_account_id', '=', self.id)], limit=1)
            bank_id = False
            json = {
                "EmployeeID":  employee_id.id,
                "Company": employee_id.company_id.name,
            }
            if vals.get('bank_id'):
                bank_id = self.env['res.bank'].browse(vals['bank_id'])
            json.update({
                "EOBankName": bank_id and bank_id.name or self.bank_id.name or "",
                "EOBankAccountNumber": vals.get('acc_number', self.acc_number) or "",
                "EOBankNameOnAccount": vals.get('acc_holder_name', self.acc_holder_name) or "",
                "EOBankType": vals.get('type', self.type) or "",
                "EOBankRoutingNumber": "",
            })
            if 'bank_id' in vals:
                json.update({"OldEOBankName": self.bank_id.name})
            if 'acc_number' in vals:
                json.update({"OldEOBankAccountNumber": self.acc_number})
            if 'acc_holder_name' in vals:
                json.update({"OldEOBankNameOnAccount": self.acc_holder_name})
            if 'type' in vals:
                json.update({"OldEOBankType": self.type})
            final_data['data'] = json
            webhook_werp_history_id = \
                self.env['webhook_werp.history'].action_webhook_werp_history_create(
                    final_data)
            if webhook_werp_history_id:
                final_data['webhook_werp_history_id'] = webhook_werp_history_id.id
                thread = threading.Thread(
                    target=webhook_werp_id.sent_data,
                    args=(webhook_werp_id.model_name, final_data, self))
                thread.start()
