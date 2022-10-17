# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SupplierEquivalentDocumentLine(models.Model):
    _name = 'supplier.equivalent.document.line'
    _description = 'Lineas del documento de soporte en adquisiciones efectudas a NO obligados a facturar'

    name = fields.Char(string="Documento")
    product_id = fields.Many2many('product.product', string='Producto')
    account_id = fields.Many2one('account.account', string='Cuenta')
    quantity = fields.Float(string='Quantity', default=1.0, digits='Product Unit of Measure')
    product_uom_id = fields.Many2one('uom.uom', string='Unidad de Medida')
    currency_id = fields.Many2one('res.currency', string='Currency')
    price_unit = fields.Float(string='Unit Price', digits='Product Price')
    discount = fields.Float(string='Discount (%)', digits='Discount', default=0.0)
    debit = fields.Monetary(string='Debit', default=0.0, currency_field='company_currency_id')
    credit = fields.Monetary(string='Credit', default=0.0, currency_field='company_currency_id')
    price_subtotal = fields.Monetary(string='Subtotal', store=True, readonly=True,
        currency_field='always_set_currency_id')
    price_total = fields.Monetary(string='Total', store=True, readonly=True,
        currency_field='always_set_currency_id')
    company_id = fields.Many2one(related='move_id.company_id', store=True, readonly=True)
    tax_base_amount = fields.Monetary(string="Base Amount", store=True, readonly=True,
        currency_field='company_currency_id')
    tax_ids = fields.Many2many('account.tax', string='Taxes', help="Taxes that apply on the base amount")
    tax_line_id = fields.Many2one('account.tax', string='Originator Tax', ondelete='restrict', store=True,
        compute='_compute_tax_line_id', help="Indicates that this journal item is a tax line")
    
    
    

    date = fields.Date(string='Fecha')
    line_ids = fields.One2many('supplier.equivalent.document.line', 'supplier_doc_id', string='Lineas')
    
    
    

    