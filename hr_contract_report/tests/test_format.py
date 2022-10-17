# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from .common import TestHrContractReportCommon


class TestFormats(TestHrContractReportCommon):

    def setUp(self):
        super(TestFormats, self).setUp()

    def test_formats(self):

        self.section_id_3 = self.ContractSection.sudo(self.hr_officer).create({
            'name': 'Section 3',
            'sequence': 3,
            'description': 'Provide section 3 details here'
        })

        self.formats_id_1 = self.ContractFormat.sudo(self.hr_officer).create({
            'name': 'Formats 1',
            'contract_section_ids': [(6, 0, [self.section_id_3.id])]
        })
