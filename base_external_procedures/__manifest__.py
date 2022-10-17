# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Base External Procedures',
    'version': '12.0.1.0.0',
    'summary': 'Base External Procedures',
    'category': 'Human Resources',
    'author': 'WSuite',
    'license': 'LGPL-3',
    'maintainer': 'WSuite',
    'company': 'WSuite SAS',
    'website': 'https://wsuite.com/',
    'depends': [
        'hr_payroll_extended_werp',
    ],
    'data': [
        "security/ir.model.access.csv",
        "views/res_external_procedures_view.xml",
        'views/hr_payroll_view.xml',
    ],
    'installable': True,
}
