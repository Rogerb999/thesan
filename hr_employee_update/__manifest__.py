# Copyright 2020-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Hr Employee Update',
    'version': '12.0.1.0.0',
    'summary': 'Hr Employee Update',
    'category': 'Administration',
    'author': 'WSuite',
    'license': 'LGPL-3',
    'maintainer': 'WSuite',
    'company': 'WSuite SAS',
    'website': 'https://wsuite.com/',
    'depends': [
        'hr',
    ],
    'data': [
        "wizard/hr_employee_update_wizard_view.xml",
        "wizard/hr_employee_update_wizard_one_view.xml",
    ],
    'installable': True,
}
