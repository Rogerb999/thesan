# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from .common import TestHrContractExtended


class TestMaritalStatus(TestHrContractExtended):

    def setUp(self):
        super(TestMaritalStatus, self).setUp()

    def test_marital_status(self):

        marital_status_id_1 = self.MaritalStatus.create({'name': 'Single'})

        self.assertFalse(self.employee_id_1.marital_status_id.id)
        self.employee_id_1.write({'marital_status_id': marital_status_id_1.id})
        self.assertEqual(self.employee_id_1.marital_status_id.name,
                         'Single', 'Marital status mismatch!')
