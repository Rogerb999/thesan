# Copyright 2020-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Hr Payroll Report Configuration',
    'version': '12.0.1.0.0',
    'summary': 'Hr Payroll Report Configuration',
    'category': 'Human Resources',
    'author': 'WSuite',
    'license': 'LGPL-3',
    'maintainer': 'WSuite',
    'company': 'WSuite SAS',
    'website': 'https://wsuite.com/',
    'depends': [
        'hr_payroll_extended_werp'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_group_values_view.xml',
        'views/hr_group_rules_view.xml',
        'views/hr_items_lines_view.xml',
        'views/hr_payroll_configuration_report_view.xml',
    ],
    'installable': True,
    'application': True,
}
