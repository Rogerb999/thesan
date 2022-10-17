# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.addons.hr.tests.common import TestHrCommon


class TestHrContractReportCommon(TestHrCommon):

    def setUp(self):
        super(TestHrContractReportCommon, self).setUp()

        self.ContractSection = self.env['contract.section']
        self.ContractFormat = self.env['contract.format']
        self.hr_officer = self.res_users_hr_officer.id
