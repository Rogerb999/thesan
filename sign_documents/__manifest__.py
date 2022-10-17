# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Signature Document',
    'version': '12.0.1.0.0',
    'author': 'WSuite',
    'maintainer': 'WSuite',
    'company': 'WSuite SAS',
    'website': 'https://wsuite.com/',
    'depends': [
                'mail',
                'portal'],
    'data': [
        'data/sign_field_type_data.xml',
        'security/sign_document_security.xml',
        'security/ir.model.access.csv',
        'views/sign_documents_asset.xml',
        'views/sign_field_type_view.xml',
        'wizard/sign_request_process_view.xml',
        'views/document_sign_template_view.xml',
        'views/sign_request_details_view.xml',
    ],
    'demo': [],
    'qweb': [
        'static/src/xml/sign_documents.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
