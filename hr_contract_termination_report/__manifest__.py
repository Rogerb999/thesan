# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'HR Contract Termination Report',
    'version': '12.0.1.0',
    'author': 'WSuite',
    'license': 'LGPL-3',
    'website': 'https://www.wsuite.com',
    'category': 'Human Resources',
    'summary': "Module to print Report of employee's Contract Termination.",
    'depends': ['hr_contract_completion',
                ],
    'data': ['views/inherited_res_company_view.xml',
             'views/inherited_res_partner_view.xml',
             'report/report_laboral_certification.xml',
             'report/report_entities_certification.xml',
             'report/report_medical_certification.xml',
             'report/report_layoffs_certification.xml',
             'report/report_answer_employee.xml',
             'report/report_confidentiality_agreement.xml',
             'report/report_hr_payslip_template.xml',
             'report/report_all_contract.xml',
             'report/hr_contract_termination_report.xml',
             ],
    'installable': True,
    'application': False
}
