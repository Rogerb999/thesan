# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta
from datetime import datetime
from odoo import fields, models, api


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    eps_id = fields.Many2one(
        'res.partner', 'EPS',
        domain="[('is_eps', '=', True)]",
        track_visibility='onchange')
    pension_fund_id = fields.Many2one(
        'res.partner', 'Pension Fund', domain="[('is_afp', '=', True)]",
        track_visibility='onchange')
    unemployment_fund_id = fields.Many2one(
        'res.partner', 'Unemployment Fund',
        domain="[('is_unemployee_fund', '=', True)]",
        track_visibility='onchange')
    arl_id = fields.Many2one(
        'res.partner', 'ARL',
        domain="[('is_arl', '=', True)]", track_visibility='onchange')
    prepaid_medicine_id = fields.Many2one(
        'res.partner', 'Prepaid Medicine',
        domain="[('is_prepaid_medicine', '=', True)]", track_visibility='onchange'
    )
    prepaid_medicine2_id = fields.Many2one(
        'res.partner', 'Prepaid Medicine 2',
        domain="[('is_prepaid_medicine', '=', True)]", track_visibility='onchange'
    )
    afc_id = fields.Many2one(
        'res.partner', 'AFC',
        domain="[('is_afc', '=', True)]", track_visibility='onchange')
    voluntary_contribution_id = fields.Many2one(
        'res.partner', 'Voluntary Contribution',
        domain="[('is_voluntary_contribution', '=', True)]",
        track_visibility='onchange')
    voluntary_contribution2_id = fields.Many2one(
        'res.partner', 'Voluntary Contribution2',
        domain="[('is_voluntary_contribution', '=', True)]",
        track_visibility='onchange')
    arl_percentage = fields.Float(
        'ARL Percentage', digits=(32, 6), track_visibility='onchange')
    medic_exam_attach = fields.Binary('Medica Exam Attachment')
    identification_id = fields.Char(related='address_home_id.vat', track_visibility='onchange')
    ident_type = fields.Selection(
        related='address_home_id.l10n_co_document_type', track_visibility='onchange')
    ident_issuance_date = fields.Date(
        'Identification Issuance Date', track_visibility='onchange')
    ident_issuance_city_id = fields.Many2one(
        'res.city', 'Identification Issuance City', track_visibility='onchange')
    permit_expire = fields.Date(track_visibility='onchange')
    attachments_count = fields.Integer(
        compute="_compute_attachments_count", string="Attachments Count")
    entry_date = fields.Date('Entry Date')
    seniority = fields.Char(compute="_compute_seniority")
    found_layoffs_id = fields.Many2one(
        'res.partner', 'Found Layoffs',
        domain="[('is_found_layoffs', '=', True)]", track_visibility='onchange')

    blood_type = fields.Selection([
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ], track_visibility='onchange')
    class_llibreta_militar = fields.Char(
        'Class Llibreta Militar', track_visibility='onchange')
    number_of_llibreta_militar = fields.Char(
        'Number of Llibreta Militar', track_visibility='onchange')
    type_of_housing = fields.Selection([
        ('propia', 'Propia'),
        ('familiar', 'Familiar'),
        ('arrendada', 'Arrendada')], 'Type of Housing', default='propia',
        track_visibility='onchange')
    stratum = fields.Char('Stratum', track_visibility='onchange')
    state_of_birth_id = fields.Many2one(
        'res.country.state',
        'State of Birth',
        domain="[('country_id', '=', country_of_birth)]",
        track_visibility='onchange')
    place_of_birth_id = fields.Many2one(
        'res.city',
        'Place of Birth',
        domain="[('country_id', '=', country_of_birth),"
               " ('state_id', '=', state_of_birth_id)]",
        track_visibility='onchange')
    birthday = fields.Date(
        'Date of Birth', groups="hr.group_hr_user",
        track_visibility='onchange')
    country_of_birth = fields.Many2one(
        'res.country', string="Country of Birth", groups="hr.group_hr_user",
        track_visibility='onchange')
    country_id = fields.Many2one(
        'res.country', 'Nationality (Country)', groups="hr.group_hr_user",
        track_visibility='onchange')
    emergency_contact = fields.Char(
        "Emergency Contact", groups="hr.group_hr_user",
        track_visibility='onchange')

    def _compute_attachments_count(self):
        for employee in self:
            domain = [('res_id', '=', employee.id),
                      ('res_model', '=', 'hr.employee')]
            attachment_obj = self.env['ir.attachment'].sudo()
            employee.attachments_count = attachment_obj.search_count(domain)


    @api.multi
    @api.depends('entry_date')
    def _compute_seniority(self):
        for employee in self:
            if employee.entry_date:
                today = str(fields.date.today()) + ' ' + '00:00:00'
                entry_date = str(employee.entry_date) + ' ' + '00:00:00'
                start = datetime.strptime(entry_date, '%Y-%m-%d %H:%M:%S')
                ends = datetime.strptime(today, '%Y-%m-%d %H:%M:%S')
                diff = relativedelta(ends, start)
                diff_str = "%d days %d month %d years" % (
                    diff.days, diff.months, diff.years)
                employee.seniority = diff_str
