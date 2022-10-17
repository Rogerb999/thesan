# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from .common import TestHrContractReportCommon


class TestSections(TestHrContractReportCommon):

    def setUp(self):
        super(TestSections, self).setUp()

    def test_sections(self):

        self.section_id_1 = self.ContractSection.sudo(self.hr_officer).create({
            'name': 'Section 1',
            'sequence': 1,
            'description': 'Provide section 1 details here'
        })

        self.section_id_2 = self.ContractSection.sudo(self.hr_officer).create({
            'name': 'Section 2',
            'sequence': 1,
            'description': 'Provide section 2 details here'
        })
