# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api, fields, _
import requests
import json
from odoo.exceptions import UserError


class HREvaluation(models.Model):
    _name = "hr.evaluation"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "HR Evaluation"
    _rec_name = 'PerCodExt'

    CoKey = fields.Char(dafault='7b9f8173-eeec-4d78-b959-dc709dac8e91')
    PerCodExt = fields.Char('Person Code', track_visibility='onchange')
    PerNom = fields.Char('Name', track_visibility='onchange')
    PerApe = fields.Char('Surname', track_visibility='onchange')
    PerNumIde = fields.Char(
        'Identification Number', track_visibility='onchange')
    PerGen = fields.Selection([
        ('M', 'Male'),
        ('F', 'Female')
    ], 'Gender', track_visibility='onchange')
    PerMail = fields.Char('Email', track_visibility='onchange')
    CoMailNot = fields.Char(
        'User Email',
        default=lambda self: self.env.user.partner_id.email)
    PcaTip = fields.Selection([
        ('A', 'Adjectives'),
        ('D', 'Descriptions')
    ], 'Type of PCA', track_visibility='onchange')
    CoRegCod = fields.Selection([
        ('es', 'Spanish'),
    ], default='es', track_visibility='onchange')
    PcaLink = fields.Char('URL for Presentation')
    PcaCod = fields.Char('Code')
    hr_applicant_id = fields.Many2one('hr.applicant', 'Applicant')
    PcaEst = fields.Selection([
        ('6', 'Incomplete'),
        ('7', 'Complete'),
    ], 'Status', default='6', track_visibility='onchange')
    PcaFec = fields.Date('Test Ended on', track_visibility='onchange')
    percentage = fields.Float('Percentage')
    document_link = fields.Char()
    PcaImg = fields.Char('URL of Evaluation')
    jca_details_id = fields.Many2one(
        'jca.details',
        'JCA')

    @api.multi
    def get_result_pca_details(self):
        headers = {'Content-type': 'application/json'}
        params = {
            'CoKey': '7b9f8173-eeec-4d78-b959-dc709dac8e91',
            'PcaCod': self.PcaCod,
            'PerCodExt': self.PerCodExt,
        }
        data_json = json.dumps(params)
        url = 'https://timshr.com/core/api/Pca/GetPcaResult'
        r = requests.post(url, data=data_json, headers=headers)
        output_data = r.json()[0]
        self.write({
            'PcaImg': output_data.get('PcaImg', False),
        })

    @api.multi
    def open_view(self):
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.evaluation',
            'res_id': self.id,
        }

    @api.onchange('jca_details_id')
    def onchange_jca_details_id(self):
        if self.jca_details_id:
            headers = {'Content-type': 'application/json'}
            params = {
                'CoKey': '7b9f8173-eeec-4d78-b959-dc709dac8e91',
                'PcaCod': self.PcaCod,
                'JcaCodExt': self.jca_details_id.code,
            }
            data_json = json.dumps(params)
            url = 'https://timshr.com/core/api/Pca/GetPcaVsJcaResult'
            r = requests.post(url, data=data_json, headers=headers)
            output_data = r.json()
            if isinstance(output_data, str):
                raise UserError(_("Code [%s] not matched in system. Please "
                                  "check it!") % (self.jca_details_id.code))
            self.document_link = output_data.get('RepLink', False)
            self.percentage = output_data.get('Val', False)

    @api.multi
    def send_mail(self):
        template_id = self.env.ref(
            'hr_recruitment_extended_werp.email_template_evaluation')
        self.env['mail.template'].browse(template_id.id).send_mail(self.id)

    @api.multi
    def create_evaluation(self):
        headers = {'Content-type': 'application/json'}
        self.PerCodExt = self.id
        params = {
            'CoKey': '7b9f8173-eeec-4d78-b959-dc709dac8e91',
            'PerCodExt': self.PerCodExt,
            'PerNom': self.PerNom,
            'PerApe': self.PerApe,
            'PerNumIde': self.PerNumIde,
            'PerGen': self.PerGen,
            'PerMail': self.PerMail,
            'CoMailNot': self.CoMailNot,
            'PcaTip': self.PcaTip,
            'CoRegCod': self.CoRegCod,
        }
        data_json = json.dumps(params)
        url = 'https://timshr.com/core/api/Pca/AddSurvey'
        r = requests.post(url, data=data_json, headers=headers)
        output_data = r.json()
        self.write({
            'PcaLink': output_data.get('PcaLink', False),
            'PcaCod': output_data.get('PcaCod'),
        })
        self.send_mail()

    @api.model
    def create(self, vals):
        res = super(HREvaluation, self).create(vals)
        res.create_evaluation()
        return res
