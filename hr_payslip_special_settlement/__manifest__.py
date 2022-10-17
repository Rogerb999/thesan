# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Payslip Settlement',
    'version': '12.0.1.0.0',
    'summary': """ """,
    'sequence': 15,
    'category': 'Human Resources',
    'author': 'WSuite',
    'license': 'LGPL-3',
    'maintainer': 'WSuite',
    'company': 'WSuite SAS',
    'website': 'https://wsuite.com/',
    'description': """
    """,
    'depends': ['hr_payroll', 'hr_novelty'],
    'data': [
        'security/ir.model.access.csv',
        'views/type_settlement_view.xml',
        'views/assign_month_view.xml',
        'views/inherited_hr_payslip_view.xml'
    ],
    'installable': True,
    'application': True,
}
