# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Resources',
    'summary': 'Resource Fee',
    'version': '12.0.1.0.0',
    'category': 'base',
    'website': 'https://wsuite.com/',
    'author': 'WSuite',
    'license': 'LGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'account',
        'hr'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/resources_fee_view.xml',
        'views/res_partner_view.xml',
    ],
}
