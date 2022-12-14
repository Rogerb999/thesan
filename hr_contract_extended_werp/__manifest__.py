# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'HR Contract Extended',
    'version': '12.0.1.0.0',
    'category': 'Generic Modules/Human Resources',
    'author': 'WSuite',
    'maintainer': 'WSuite',
    'company': 'WSuite SAS',
    'website': 'https://wsuite.com/',
    'depends': [
                'hr_contract',
                'hr_recruitment',
                'hr_extended',
                #'hr_curriculum_vitae',
                #'sign_documents',
    ],
    'data': [
        'security/ir.model.access.csv',
        'report/contract_format_aprendiz_report.xml',
        'report/contract_format_fijo_report.xml',
        'report/contrato_indefibido_integral_report.xml',
        'report/contrato_indefibido_report.xml',
        'report/contrato_practicante_report.xml',
        'report/contrato_practicas_report.xml',
        'report/contract_format_report.xml',
        'views/res_company_view.xml',
        'views/res_users_view.xml',
        'views/hr_marital_status_view.xml',
        'views/hr_center_formation_view.xml',
        'views/hr_contract_reson_change_view.xml',
        'views/hr_employee_view.xml',
        'views/mail_compose_message_view.xml',
        'wizard/reason_change_wizard_view.xml',
        'views/hr_contract_view.xml',
        'data/contract_mail_data.xml',
        'wizard/create_contract_identification_wizard_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
