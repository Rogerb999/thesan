# -*- coding: utf-8 -*-

{
    'name': 'Close Novelty for payroll',
    'version': '12.0.1.0',
    'author': 'WSuite',
    'license': 'LGPL-3',
    'website': 'https://www.wsuite.com',
    'category': 'base',
    'summary': "Module to manage events alerts",
    'depends': ['base',
                'mail',
                'hr_novelty',
                'hr_payroll',
                ],
    'data': [
        'views/close_event_view.xml',
        'views/hr_leave_view.xml',
        'views/hr_novelty_view.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False
}
