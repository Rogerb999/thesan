# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import json
import io
from reportlab.pdfgen import canvas
from PyPDF2 import PdfFileReader, PdfFileWriter
import base64
from reportlab.lib.utils import ImageReader
from odoo.exceptions import UserError


class SignRequestDetails(models.Model):
    _name = 'sign.request.details'
    _description = 'Sign Request Details'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.model
    def _group_expand_states(self, states, domain, order):
        return [key for key, val in type(self).state.selection]

    template_id = fields.Many2one(
        'document.sign.template', track_visibility='onchange')
    name = fields.Char(
        'Name', required=True, track_visibility='onchange')
    request_user_ids = fields.One2many(
        'sign.request.user.list', 'sign_request_user_id')
    state = fields.Selection([
        ('sent', 'Sent'),
        ('signed', 'Signed'),
        ('cancel', 'Canceled')
    ], group_expand='_group_expand_states', track_visibility='onchange')
    sign_document = fields.Binary("Sign Document", track_visibility='onchange')
    datas_fname = fields.Char("File Name")
    check_eligibility = fields.Boolean(
        compute='_compute_check_eligibility')
    reference_model = fields.Char('Reference Model')
    reference_id = fields.Char('Reference Id')

    def _compute_check_eligibility(self):
        for record in self:
            record.check_eligibility = False
            if self.env.user.partner_id in \
                    record.request_user_ids.mapped('partner_id'):
                record.check_eligibility = True

    @api.multi
    def edit_template(self):
        return {
            'name': self.template_id.attachment_id.name,
            'type': 'ir.actions.client',
            'tag': 'sign_documents.pdf_template',
            'context': {
                'id': self.template_id.id,
                'edit': False,
                'request_id': self.id,
                'request_state': self.state
            },
        }

    @api.multi
    def get_bytesIO(self, datas):
        return io.BytesIO(base64.b64decode(datas))

    @api.multi
    def update_with_pdf_document(self, requestId, items):
        json_data = json.loads(items)
        SignDocumentItem = self.env['sign.document.item']
        for d in json_data:
            sign_document_item_id = SignDocumentItem.browse(d['id'])
            if not sign_document_item_id.value and not \
                    sign_document_item_id.signature:
                return False
        request_id = self.env['sign.request.details'].browse(requestId)
        if self.env.user.partner_id not in \
                request_id.request_user_ids.mapped('partner_id'):
            raise UserError(_("You are not eligible for sign "
                              "this document.Only defines user "
                              "partner sign this document!"))
        # Reference: https://pythonhosted.org/PyPDF2/PdfFileReader.html
        packetIO = io.BytesIO()
        original_document = PdfFileReader(
            request_id.get_bytesIO(
                request_id.template_id.attachment_id.datas))
        can = canvas.Canvas(packetIO)
        page_number = original_document.getNumPages()
        for p_no in range(0, page_number):
            mediabox = original_document.getPage(p_no).mediaBox
            mediabox_width = mediabox.getWidth()
            mediabox_height = mediabox.getHeight()
            check_initial = False
            for d in json_data:
                sign_document_item_id = SignDocumentItem.browse(d['id'])
                mwPX = mediabox_width * d['pos_X']
                mhPS = mediabox_height * (1 - d['pos_Y'] - d['item_height'])
                if p_no + 1 == d['page']:
                    if sign_document_item_id.signature:
                        request_id.set_signature(
                            sign_document_item_id, can, mwPX,
                            mhPS, mediabox_width, mediabox_height,
                            d['item_width'], d['item_height'])
                    elif sign_document_item_id.value:
                        can.drawString(mwPX, mhPS, sign_document_item_id.value)
                if not check_initial and sign_document_item_id.\
                        sign_field_type_id.sign_type == 'initial':
                    check_initial = True
                    request_id.set_signature(
                        sign_document_item_id, can, mwPX, mhPS,
                        mediabox_width, mediabox_height,
                        d['item_width'], d['item_height'])
            can.showPage()
        can.save()
        reader = PdfFileReader(packetIO)
        writer = PdfFileWriter()
        for request_user_id in request_id.request_user_ids:
            if request_user_id.partner_id == self.env.user.partner_id:
                request_user_id.state = 'signed'
        for p_no in range(0, page_number):
            od_page = original_document.getPage(p_no)
            od_page.mergePage(reader.getPage(p_no))
            writer.addPage(od_page)
        state_details = request_id.mapped(
            'request_user_ids').filtered(lambda m: m.state == 'signed')
        if len(request_id.request_user_ids) == len(state_details):
            request_id.state = 'signed'
        output = io.BytesIO()
        writer.write(output)
        document = base64.b64encode(output.getvalue())
        request_id.write({
            'sign_document': document,
            'datas_fname': request_id.name
        })
        if request_id.reference_model == 'hr.contract':
            reference_id = \
                self.env[request_id.reference_model].browse(
                    int(request_id.reference_id))
            reference_id.write({
                'signed_contract': document,
                'datas_fname': request_id.name
            })
        output.close()
        return True

    @api.multi
    def set_signature(self, sign_document_item_id, can, mwPX, mhPS,
                      mediabox_width, mediabox_height,
                      item_width, item_height):
        image_reader = \
            ImageReader(self.get_bytesIO(
                sign_document_item_id.signature))
        can.drawImage(
            image_reader, mwPX, mhPS,
            width=mediabox_width * item_width,
            height=mediabox_height * item_height,
            mask='auto')


class SignRequestUserList(models.Model):
    _name = 'sign.request.user.list'
    _description = 'Sign Request User List'
    _rec_name = 'partner_id'

    sign_request_user_id = fields.Many2one(
        'sign.request.details', required=True)
    partner_id = fields.Many2one('res.partner', required=True)
    email = fields.Char(related='partner_id.email')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Waiting'),
        ('signed', 'Signed')
    ])
