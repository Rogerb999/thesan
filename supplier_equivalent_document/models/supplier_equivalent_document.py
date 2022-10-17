# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SupplierEquivalentDocument(models.Model):
    _name = 'supplier.equivalent.document'
    _description = 'Documento de soporte en adquisiciones efectudas a NO obligados a facturar'

    name = fields.Char(string="Documento")
    partner_id = fields.Many2many('res.partner', string='Proveedor')
    date = fields.Date(string='Fecha')
    line_ids = fields.One2many('supplier.equivalent.document.line', 'supplier_doc_id', string='Lineas')
    
    
    

    