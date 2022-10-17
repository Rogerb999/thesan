# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Recruitment Reasons WSuite',
    'version': '12.0.1.0.0',
    'summary': 'Recruitment Reasons Customization for WSuite',
    'category': 'Human Resources',
    'author': 'WSuite',
    'license': 'LGPL-3',
    'maintainer': 'WSuite',
    'company': 'WSuite SAS',
    'website': 'https://wsuite.com/',
    'depends': [
               'hr_recruitment',
    ],
    'data': [
        'views/recruitment_reason_view.xml',
        'views/inherited_recruitment_reason_view.xml',
        'views/job_position_view.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
