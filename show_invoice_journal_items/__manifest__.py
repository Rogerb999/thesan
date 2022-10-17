# -*- coding: utf-8 -*-
# Copyright 2020 CorTex IT Solutions Ltd. (<https://cortexsolutions.net/>)
# License AGPL-3

{
    'name': "Show Invoices/Bills Journal Items",

    'summary': """
        This module enable you to show Invoices/Bills Journal Items in form views for users who have "Show Full Accounting Features" access.
        """,
    'description': """
Invoice journal items
Invoice journal entry
journal items
journal entry
bill journal items
bill journal entry
journal
show journal items
    """,

    'author': 'CorTex IT Solutions Ltd.',
    'website': 'https://cortexsolutions.net',
    'license': 'AGPL-3',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting & Finance',
    'version': '12.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['account'],
    # always loaded
    'data': [
        'views/account_invoice_views.xml',
    ],
    'images': ['static/description/main_screenshot.png'],
    "installable": True
}
