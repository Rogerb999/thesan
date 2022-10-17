# -*- coding: utf-8 -*-
# from odoo import http


# class SupplierEquivalentDocument(http.Controller):
#     @http.route('/supplier_equivalent_document/supplier_equivalent_document/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/supplier_equivalent_document/supplier_equivalent_document/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('supplier_equivalent_document.listing', {
#             'root': '/supplier_equivalent_document/supplier_equivalent_document',
#             'objects': http.request.env['supplier_equivalent_document.supplier_equivalent_document'].search([]),
#         })

#     @http.route('/supplier_equivalent_document/supplier_equivalent_document/objects/<model("supplier_equivalent_document.supplier_equivalent_document"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('supplier_equivalent_document.object', {
#             'object': obj
#         })
