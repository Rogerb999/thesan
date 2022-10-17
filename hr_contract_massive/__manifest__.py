# Copyright 2020-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'HR Contract Massive',
    'version': '12.0.1.0.0',
    'category': 'Generic Modules/Human Resources',
    'author': 'WSuite',
    'maintainer': 'WSuite',
    'company': 'WSuite SAS',
    'website': 'https://wsuite.com/',
    'depends': [
                'hr_contract_extended_werp',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/hr_contract_massive_data.xml',
        'views/hr_contract_massive_view.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
