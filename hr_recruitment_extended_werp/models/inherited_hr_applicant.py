# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
import requests
import json
import datetime
from odoo.exceptions import ValidationError


class HrApplicant(models.Model):
    """Extends HR Applicant Functionality."""

    _inherit = "hr.applicant"

    reason_id = fields.Many2one('reason.disqualification',
                                string='Disqualification Reason')
    level_academic = fields.Selection([
        ('bachelor', 'Bachelor'),
        ('technical', 'Technical'),
        ('undergraduate', 'Undergraduate'),
        ('specialization', 'Specialization'),
        ('master', 'Master'),
        ('doctorate', 'Doctorate'),
        ('other', 'Other'),
    ])
    is_working = fields.Boolean(string='Is Working')
    working_witn_group = fields.Boolean()
    company_group_id = fields.Many2one('res.partner')
    reason_renounce_id = fields.Many2one('hr.reason.changed')
    other_recruitment_group = fields.Boolean()
    hr_application_id = fields.Many2one('hr.applicant')
    date_application = fields.Datetime(related='hr_application_id.create_date',
                                       string='Application Date', store=True)
    salary_present = fields.Float(string='Salary')
    group_experience_age = fields.Float()
    experience_age = fields.Float()
    evaluation_ids = fields.One2many(
        'hr.evaluation',
        'hr_applicant_id',
        'HR Evaluation Details')
    check_evaluation = fields.Boolean(
        related='stage_id.add_evaluation',
        string="Check Evaluation")

    @api.multi
    def create_employee_from_applicant(self):
        """Other application should in cerrado por fin del proceso."""
        res = super(HrApplicant, self).create_employee_from_applicant()
        for applicant in self.env['hr.applicant'].search([
                ('id', '!=', self.id),
                ('partner_id', '!=', self.partner_id.id),
                ('job_id', '=', self.job_id.id)]):
            applicant.stage_id = self.env.ref(
                'hr_recruitment_extended_werp.stage_job11').id
            applicant.partner_id.write({'state_selection': 'eligible'})
        return res

    @api.multi
    def archive_applicant(self):
        """Add validation while archive application."""
        # Overwrite Function which is in the hr_recruitment.
        # Because Task 10593
        # The reason for overwrite is while select state of
        # the parther then and then archive_applicant should
        # apply
        # super(HrApplicant, self).archive_applicant()
        # The portion of the code for is in the
        # action_select_state method which is in
        # partner.state.selection.wizard model
        if not self.reason_id:
            raise ValidationError(_(
                'Please add Disqualification Reason.'))
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'partner.state.selection.wizard',
            'target': 'new',
            'context': {
                'default_state_selection': self.partner_id.state_selection},
        }

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        """Onchange on Partner for state selection."""
        super(HrApplicant, self).onchange_partner_id()
        if self.partner_id:
            self.partner_id.write({
                'postulant': True,
                'state_selection': 'in_process',
            })
            self.partner_name = self.partner_id.name
            self.name = self.partner_id.name

    @api.multi
    def create_and_get_data(self):
        ctx = dict(self.env.context or {})
        ctx.update({
            'default_PerNom': self.partner_id.first_name,
            'default_PerApe': self.partner_id.surname,
            'default_PerMail': self.partner_id.email,
            'default_hr_applicant_id': self.id,
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.evaluation',
            'context': ctx
        }
