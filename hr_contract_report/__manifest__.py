# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'HR Contract Report',
    'version': '12.0.1.0.0',
    'category': 'Generic Modules/Human Resources',
    'author': 'WSuite',
    'maintainer': 'WSuite',
    'company': 'WSuite SAS',
    'website': 'https://wsuite.com/',
    'depends': [
                'hr_contract',
                'hr_recruitment',
    ],
    'data': [
        'views/contract_section_views.xml',
        'views/contract_format_views.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
