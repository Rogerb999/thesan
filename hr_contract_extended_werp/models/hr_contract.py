# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta


class HrContract(models.Model):
    _inherit = 'hr.contract'

    subcontract = fields.Boolean('Subcontract?')
    father_contract_id = fields.Many2one(
        'hr.contract', 'Father Contract')
    reason_change_id = fields.Many2one(
        'hr.contract.reason.change', 'Reason Change',
        copy=False)
    signed_contract = fields.Binary(
        string='Signed Contract')
    ret_fue_2 = fields.Float('Retention Font 2')
    integral_salary = fields.Boolean('Integral Salary')
    contribution_pay = fields.Boolean('Contribution Pay')
    datas_fname = fields.Char("File Name")
    speciality_id = fields.Many2one('hr.cv.academic.studies', 'Speciality')
    institution_id = fields.Many2one('hr.academic.institution', 'Institution')
    center_formation_id = fields.Many2one(
        'hr.center.formation', 'Center Formation')
    currency_id = fields.Many2one(
        'res.currency', related='', string='Currency')
    is_required_you = fields.Boolean('Required You')
    description = fields.Text()

    @api.multi
    @api.constrains('state', 'employee_id')
    def check_contracts(self):
        if self.employee_id.required_restriction:
            for contract in self:
                contract_ids = self.search([
                    ('state', '=', 'open'),
                    ('employee_id', '=', contract.employee_id.id),
                    ('id', '!=', contract.id)])
                if contract_ids and contract.state == 'open':
                    raise ValidationError(_('An employee can not have 2 '
                                            'contracts in Running state!'))
                if not contract.signed_contract and contract.state == 'open':
                    raise ValidationError(_(
                        'The contract can not be placed'
                        ' in the "Running" state!'))

    @api.multi
    @api.constrains('employee_id')
    def check_employee_details(self):
        if self.employee_id.required_restriction:
            for contract in self:
                data = contract.employee_id.read([
                    'photos_white_background', 'photo_black_white',
                    'photocopy_document_indentity', 'photocopy_militar_card',
                    'cut_past', 'photocopy_of_the_certificate',
                    'format_referencing_last_job', 'photocopy_last_job',
                    'photocopy_of_the_eps_certificate',
                    'photocopies_pensiones',
                    'photocopy_layoffs', 'bank_certification',
                    'certificate_income_withholdings', 'renta_estado',
                    'format_references', 'medic_exam_attach', 'medic_exam',
                    'eps_id', 'pension_fund_id', 'unemployment_fund_id',
                    'arl_id', 'prepaid_medicine_id'])[0]
                if not all(data.values()) and contract.state == 'pending':
                    raise ValidationError(_(
                        'Please, fill the required details in an '
                        'employee of %s!') % self.employee_id.name)

    @api.multi
    def write(self, vals):
        self.check_employee_details()
        if vals.get('state') == 'open':
            self.employee_id.write({
                'job_id': vals.get('job_id', False) or self.job_id.id,
                'job_title': vals.get('job_id', False) or self.job_id.name})
        if self.employee_id.required_restriction:
            if vals.get('state') == 'open' and self.father_contract_id:
                new_date = \
                    self.father_contract_id.date_end - timedelta(
                        days=1) if self.father_contract_id.date_end else False
                self.father_contract_id.write({
                    'date_end': new_date, 'state': 'close'})
        return super(HrContract, self).write(vals)

    @api.multi
    def get_user_id(self, id):
        contract = self.env['hr.contract'].browse(id)
        return contract.employee_id.user_id.partner_id.id

    @api.onchange('struct_id')
    def onchange_struct_id(self):
        """Fill one2many based on contract type."""
        salary_rule_id = self.env['hr.salary.rule'].search(
            [('autocomplete_flex', '=', True)], limit=1)
        if self.struct_id.type_id.name == 'Nuevo Flex' and salary_rule_id:
            salary_rule_id = self.env['hr.contract.flex_wage'].create(
                {'salary_rule_id': salary_rule_id.id})
            if self.wage > 0 and self.fix_wage_amount > 0 and\
                    self.wage > self.fix_wage_amount:
                salary_rule_id.write(
                    {'amount': self.wage - self.fix_wage_amount})
            return {'value': {'flex_wage_ids': salary_rule_id.ids}}

    @api.onchange('job_id')
    def _onchange_job_id(self):
        if self.job_id and self.state == 'open':
            self.employee_id.write({
                'job_id': self.job_id.id, 'job_title': self.job_id.name})

    @api.onchange('state')
    def onchange_state(self):
        """Subcontract is Open original contract expired."""
        for contract in self:
            if contract.state == 'open':
                contract.employee_id.write(
                    {'job_id': contract.job_id.id,
                     'job_title': contract.job_id.name})
            if contract.subcontract and contract.father_contract_id and\
                    contract.state == 'open':
                contract.father_contract_id.write({'state': 'close'})

    # @api.multi
    # def action_send_contract(self):
    #     '''
    #     This function opens a window to compose an email,
    #     with the CONTRATO APRENDIZ template message loaded by default
    #     '''
    #     self.ensure_one()
    #     ir_model_data = self.env['ir.model.data']
    #     try:
    #         template_id = ir_model_data.get_object_reference(
    #             'hr_contract_extended_werp',
    #             'email_template_apprenticeship_contract')[1]
    #     except ValueError:
    #         template_id = False
    #     try:
    #         compose_form_id = ir_model_data.get_object_reference(
    #             'hr_contract_extended_werp',
    #             'email_compose_message_wizard_form_contract_extended')[1]
    #     except ValueError:
    #         compose_form_id = False
    #     ctx = {
    #         'default_model': 'hr.contract',
    #         'default_res_id': self.ids[0],
    #         'default_use_template': bool(template_id),
    #         'default_template_id': template_id,
    #         'default_composition_mode': 'comment',
    #         'force_email': True
    #     }
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'res_model': 'mail.compose.message',
    #         'views': [(compose_form_id, 'form')],
    #         'view_id': compose_form_id,
    #         'target': 'new',
    #         'context': ctx
    #     }
