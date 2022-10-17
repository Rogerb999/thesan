# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Alert Finish Contract',
    'version': '12.0.1.0.0',
    'summary': 'Alert Finish Contract',
    'category': 'Human Resources',
    'author': 'WSuite',
    'license': 'LGPL-3',
    'maintainer': 'WSuite',
    'company': 'WSuite SAS',
    'website': 'https://wsuite.com/',
    'depends': [
        'hr_payroll',
    ],
    'data': [
        "security/ir.model.access.csv",
        "views/alert_finish_contract_view.xml",
    ],
    'installable': True,
}
