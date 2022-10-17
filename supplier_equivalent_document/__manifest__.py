# -*- coding: utf-8 -*-
{
    'name': "supplier_equivalent_document",

    'summary': """
        documento soporte""",

    'description': """
        Long description of module's purpose
    """,

    'author': "",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'report/supplier_equivalent_document_reports.xml',
        'report/supplier_equivalent_document_templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
