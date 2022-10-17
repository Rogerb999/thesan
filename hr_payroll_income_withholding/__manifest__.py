# -*- coding: utf-8 -*-

{
    'name': 'Payroll Income Withholding',
    'version': '12.0.1.0',
    'author': 'WSuite',
    'website': 'https://www.wsuite.com',
    'category': 'Human Resources',
    'summary': "Module to manage income withholding in payroll of employee",
    'depends': ['base',
                'mail',
                'hr',
                'hr_payroll',
                'base_product',
                'hr_novelty',
                ],
    'data': [
        'data/ir_cron_data.xml',
        'data/hr_payroll_income_withholding_data.xml',
        'views/hr_payroll_income_withholding_view.xml',
        'views/hr_novelty_view.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
