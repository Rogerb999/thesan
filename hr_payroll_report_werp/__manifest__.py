# Copyright 2020-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Hr Payroll Report',
    'version': '12.0.1.0.0',
    'author': 'WSuite',
    'summary': 'Hr Payroll Report Customization for werp',
    'category': 'Human Resources',
    'license': 'LGPL-3',
    'maintainer': 'werp',
    'company': 'WSuite',
    'website': 'https://wsuite.com',
    'depends': [
        'werp_apps_install',
        'hr_payroll',
        'hr_extended',
        'partner_product'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_payroll_bancos_view.xml',
        'views/pago_nomina_report_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
