# Copyright 2020-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Hr Employee Flextime',
    'version': '12.0.1.0.0',
    'summary': 'Hr Employee Flextime',
    'category': 'Human Resources',
    'author': 'WSuite',
    'license': 'LGPL-3',
    'maintainer': 'WSuite',
    'company': 'WSuite SAS',
    'website': 'https://wsuite.com/',
    'depends': [
        'hr'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/hr_employee_flextime_data.xml',
        'views/hr_employee_flextime_view.xml',
        'views/inherited_hr_employee_view.xml',
    ],
    'installable': True,
}
