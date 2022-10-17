# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from .common import TestHrContractExtended
from datetime import timedelta


class TestContract(TestHrContractExtended):

    def setUp(self):
        super(TestContract, self).setUp()

    def test_contract(self):

        # Make a Subcontract
        reason_change_wizard = \
            self.env['reason.change.wizard'].with_context({
                'active_ids': [self.contract_id.id],
                'active_id': self.contract_id.id}
            ).create({
                'reason_change_id': self.reason_change_id_2.id
            })

        reason_change_wizard.create_subcontract()
        new_contract_id = self.Contract.search([
            ('father_contract_id', '=', self.contract_id.id)])

        self.assertEqual(self.contract_id.reason_change_id,
                         self.reason_change_id_2,
                         'Reason change not set properly!')

        self.assertEqual(new_contract_id.subcontract,
                         True, 'Subcontract not proper done!')

        self.assertEqual(new_contract_id.father_contract_id.id,
                         self.contract_id.id,
                         'Father contract not set proper!')

        new_contract_id.state = 'open'

        self.assertEqual(new_contract_id.date_end,
                         self.contract_id.date_end + timedelta(days=1),
                         'Father contract end date will be one day before!')

        self.assertEqual(self.contract_id.state,
                         'close', 'Father contract must be in expired state!')

    def test_send_contract(self):
        contract_details = self.contract_id.action_send_contract()

        message_count = len(self.contract_id.message_ids)
        if contract_details and contract_details.get('context'):
            self.assertEqual(
                self.email_template_id.id,
                contract_details['context']['default_template_id'],
                'Template: Contract template mis-match')

        composer = self.env['mail.compose.message'].sudo().with_context({
            'default_composition_mode': 'comment',
            'default_model': 'hr.contract',
            'default_res_id': self.contract_id.id,
            'default_template_id': self.email_template_id.id,
        }).create({
            'subject': 'Contract',
            'body': 'Here is in attachment your contract'
                    'Do not hesitate to contact us if you have any question.'
                    'Best regards'})

        # onchange and send emails
        values = composer.onchange_template_id(
            self.email_template_id.id,
            'comment',
            self.contract_id.name,
            self.contract_id.id)['value']
        composer.write(values)
        composer.send_mail()
        self.assertEqual(len(self.contract_id.message_ids), message_count + 1,
                         'Message: Message not add in chat of hr.contract')
