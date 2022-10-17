# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    marital_status_id = fields.Many2one('hr.marital.status', string="Marital",
                                        track_visibility='onchange')
    photos_white_background = fields.Binary(string='Photos White Background')
    photo_black_white = fields.Binary(string='Photos Black White')
    photocopy_document_indentity = fields.Binary(
        string='Photocopy Document Indentity')
    photocopy_militar_card = fields.Binary(string='Photocopy Militar Card')
    cut_past = fields.Binary(string='Cut Past')
    photocopy_of_the_certificate = fields.Binary(
        string='Photocopy of the Certificate')
    format_referencing_last_job = fields.Binary(
        string='Format Referencing Last Job')
    photocopy_last_job = fields.Binary(string='Photocopy Last Job')
    photocopy_of_the_eps_certificate = fields.Binary(
        string='Photocopy of the EPS Certificate')
    photocopies_pensiones = fields.Binary(string='Photocopies Pensiones')
    photocopy_layoffs = fields.Binary(string='Photocopy Layoffs')
    bank_certification = fields.Binary(string='Bank Certification')
    certificate_income_withholdings = fields.Binary(
        string='Certificate  Income Withholdings')
    renta_estado = fields.Binary(string='Renta Estado Declaración de renta')
    format_references = fields.Binary(string='Format References')
    required_restriction = fields.Boolean('Required Restriction', defautl=True,
                                          track_visibility='onchange')

    @api.multi
    def check_previous_attachment(self, attachment_obj, vals, field_name):
        name = self._fields[field_name].string
        previous_attachment_id = attachment_obj.search([
            ('name', '=', name),
            ('res_id', '=', self.id),
            ('res_model', '=', 'hr.employee')])
        previous_attachment_id.unlink()

    @api.multi
    def create_document_attachments(self, attachment_obj, vals, field_name):
        name = self._fields[field_name].string
        image = vals[field_name]
        self.check_previous_attachment(attachment_obj, vals, field_name)
        attachment_obj.create({
            'name': name,
            'datas': image,
            # 'datas_fname': name,
            'res_model': 'hr.employee',
            'res_id': self.id,
        })

    @api.multi
    def create_update_attachment(self, vals):
        attachment_obj = self.env['ir.attachment']
        document_list = [
            'photos_white_background', 'photo_black_white',
            'photocopy_document_indentity', 'photocopy_militar_card',
            'cut_past', 'photocopy_of_the_certificate',
            'format_referencing_last_job', 'photocopy_last_job',
            'photocopy_of_the_eps_certificate', 'photocopies_pensiones',
            'photocopy_layoffs', 'bank_certification',
            'certificate_income_withholdings', 'renta_estado',
            'format_references']
        for field in document_list:
            if vals.get(field):
                self.create_document_attachments(attachment_obj, vals, field)
            elif field in vals.keys():
                self.check_previous_attachment(attachment_obj, vals, field)

    @api.model
    def create(self, vals):
        res = super(HrEmployee, self).create(vals)
        res.create_update_attachment(vals)
        return res

    @api.multi
    def write(self, vals):
        self.create_update_attachment(vals)
        return super(HrEmployee, self).write(vals)

    @api.onchange('user_id')
    def _onchange_user(self):
        if self.user_id:
            self.update(self._sync_user(self.user_id))

    def _sync_user(self, user):
        vals = dict()
        if user.tz:
            vals['tz'] = user.tz
        return vals

    @api.multi
    def create_user(self):
        user_id = self.env['res.users'].create({
            'name': self.name,
            'login': self.work_email,
            'employee_id': self.id,
        })
        partner = user_id.partner_id
        user_id.write({'partner_id': self.address_home_id.id})
        partner.unlink()
        self.write({
            'user_id': user_id.id,
            'address_home_id': user_id.partner_id.id})
