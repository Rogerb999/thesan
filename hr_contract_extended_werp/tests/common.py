# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.addons.hr.tests.common import TestHrCommon
import base64
from odoo import modules
from datetime import datetime
from dateutil.relativedelta import relativedelta


class TestHrContractExtended(TestHrCommon):

    def setUp(self):
        super(TestHrContractExtended, self).setUp()

        self.HrEmployee = self.env['hr.employee']
        self.MaritalStatus = self.env['hr.marital.status']
        self.Contract = self.env['hr.contract']
        self.ContractReasonChange = self.env['hr.contract.reason.change']
        self.hr_officer = self.res_users_hr_officer.id
        self.company_id = self.env['res.company'].create({
            'name': 'Test Company'})
        self.test_partner_id = self.env['res.partner'].create({
            'name': 'Test Partner'})
        self.email_template_id = self.env.ref(
            'hr_contract_extended_werp.email_template_apprenticeship_contract')

        image_path = modules.get_module_resource(
            'hr', 'static/src/img', 'default_image.png')
        test_image = base64.b64encode(open(image_path, 'rb').read())

        employee_dict = {
            'name': 'Test Employee',
            'gender': 'male',
            'birthday': '1985-08-01',
            'medic_exam': datetime.now(),
            'eps_id': self.test_partner_id.id,
            'pension_fund_id': self.test_partner_id.id,
            'unemployment_fund_id': self.test_partner_id.id,
            'arl_id': self.test_partner_id.id,
            'prepaid_medicine_id': self.test_partner_id.id,
        }
        employee_dict.update(dict.fromkeys([
            'photos_white_background', 'photo_black_white',
            'photocopy_document_indentity', 'photocopy_militar_card',
            'cut_past', 'photocopy_of_the_certificate',
            'format_referencing_last_job', 'photocopy_last_job',
            'photocopy_of_the_eps_certificate', 'photocopies_pensiones',
            'photocopy_layoffs', 'bank_certification',
            'certificate_income_withholdings', 'renta_estado',
            'format_references', 'medic_exam_attach'], test_image))

        self.employee_id_1 = self.HrEmployee.create(employee_dict)

        self.reason_change_id_1 = self.ContractReasonChange.create({
            'name': 'Reason 1',
            'description': 'Details of reason 2'})
        self.reason_change_id_2 = self.ContractReasonChange.create({
            'name': 'Reason 2',
            'description': 'Details of reason 2'})

        self.contract_data = dict(
            name='Test Contract',
            wage=10,
            fix_wage_amount=10,
            employee_id=self.employee_id_1.id,
            state='draft',
            date_start=datetime.now() + relativedelta(days=-50),
            date_end=datetime.now() + relativedelta(days=10),
            signed_contract=test_image)

        self.contract_id = self.Contract.create(self.contract_data)
