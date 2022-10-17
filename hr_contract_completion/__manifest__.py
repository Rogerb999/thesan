# -*- coding: utf-8 -*-

{
    'name': 'hr_contract_completion',
    'version': '12.0.1.0',
    'author': 'WSuite',
    'license': 'LGPL-3',
    'website': 'https://www.wsuite.com',
    'category': 'Human Resources',
    'summary': "Module to manage employee's Contract Completion.",
    'depends': ['base',
                'mail',
                'hr_payroll',
                'hr_novelty',
                ],
    'data': ['data/hr_contract_completion_data.xml',
             'views/hr_contract_completion_view.xml',
             'views/payslip_view.xml',
             'views/inherited_hr_novelty_view.xml',
             'views/inherited_hr_contract_view.xml',
             'wizard/contract_completion_reverse_wizard_view.xml',
             'security/ir.model.access.csv',
             ],
    'installable': True,
    'application': False
}
