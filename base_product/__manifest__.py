# -*- coding: utf-8 -*-
# Copyright 2019-TODAY Victor Inojosa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Base ERP Product',
    'summary': 'Basic Configurations for ERP Product',
    'version': '12.0.1.0.0',
    'category': 'base',
    'website': 'https://wsuite.com/',
    'author': 'WSuite',
    'license': 'LGPL-3',
    'application': False,
    'installable': True,
    'external_dependencies': {
        'python': [],
        'bin': [],
    },
    'depends': [
        'base',
        #'base_address_city',
        'hr',
    ],
    'data': [
        'views/res_city_view.xml',
        'views/inherited_res_users.xml',
        'security/groups.xml',
    ],
}
