# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Base Extended',
    'summary': 'Added new field in base model',
    'version': '12.0.1.0.0',
    'category': 'base',
    'website': 'https://wsuite.com/',
    'author': 'WSuite',
    'license': 'LGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'base', 'webhook_werp', 'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/groups.xml',
        'views/ir_model_view.xml',
        'views/res_groups_view.xml',
        # 'views/res_users_view.xml',
        'views/base_import_templates.xml',
        'views/res_company_view.xml',
        'views/account_tax_view.xml',
        'views/search_fields_config_view.xml',
        'views/search_sub_fields_config_view.xml',
        'views/inherited_ir_actions_server.xml',
        'views/inherited_mail_view.xml',
    ],
}
