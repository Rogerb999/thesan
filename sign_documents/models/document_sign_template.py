# -*- coding: utf-8 -*-

from odoo import models, fields, api


class DocumentSignTemplate(models.Model):
    _name = 'document.sign.template'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Document Sign Template'
    _rec_name = 'file_name'

    attachment_id = fields.Many2one(
        'ir.attachment', 'Attachment', track_visibility='onchange')
    datas = fields.Binary(related='attachment_id.datas')
    file_name = fields.Char('File Name', track_visibility='onchange')
    sign_document_item_ids = fields.One2many(
        'sign.document.item', 'template_id', string="Signature")

    @api.multi
    def upload_selected_document(self, file_name, file_type, datas=None):
        datas = datas[datas.find(',') + 1:]
        attachment_id = self.env['ir.attachment'].create({
            'name': file_name,
            'datas_fname': file_name,
            'datas': datas,
            'res_model': 'document.sign.template',
        })
        template_id = self.env['document.sign.template'].create({
            'attachment_id': attachment_id.id,
            'file_name': file_name
        })
        return {
            'template_id': template_id.id,
            'file_name': file_name
        }

    @api.multi
    def edit_template(self):
        self.ensure_one()
        return {
            'name': self.attachment_id.name,
            'type': 'ir.actions.client',
            'tag': 'sign_documents.pdf_template',
            'context': {'id': self.id},
        }

    @api.model
    def get_details(self, template_id=None):
        template = self.browse(template_id)
        attachment = template.attachment_id.read()
        template = template.read()
        sign_fields_items = self.env['sign.document.item'].search_read(
            [('template_id', '=', template_id[0])])
        return template, sign_fields_items, attachment[0]

    @api.model
    def update_sign_document_items(self, template_id=None,
                                   sign_document_item=None):
        template = self.browse(template_id)
        template.sign_document_item_ids.unlink()
        sign_document_item_obj = self.env['sign.document.item']
        for sign_item in sign_document_item.values():
            sign_document_item_obj.create(sign_item)
        return template.id


class SignDocumentItem(models.Model):
    _name = "sign.document.item"
    _description = "Sign Document Item"

    name = fields.Char("Field Name")
    value = fields.Char("Field Value")
    template_id = fields.Many2one('document.sign.template', "Template")
    sign_field_type_id = fields.Many2one('sign.field.type', "Type")
    page = fields.Integer("Document Page", default=1)
    item_width = fields.Float(digits=(16, 2))
    item_height = fields.Float(digits=(16, 2))
    pos_X = fields.Float("Position X", digits=(16, 2))
    pos_Y = fields.Float("Position Y", digits=(16, 2))
    signature = fields.Binary('Signature', copy=False, attachment=True)

    @api.multi
    def set_document_item_value(self, template_id, height,
                                width, pos_y, pos_x, value,
                                signature, deletedata):
        sign_document_item_id = self.env['sign.document.item'].search([
            ('template_id', '=', int(template_id)),
            ('item_height', '=', float(height)),
            ('item_width', '=', float(width)),
            ('pos_Y', '=', float(pos_y)),
            ('pos_X', '=', float(pos_x))
        ])
        if sign_document_item_id:
            if deletedata:
                sign_document_item_id.unlink()
            else:
                sign_document_item_id.write({
                    'value': value, 'signature': signature})
