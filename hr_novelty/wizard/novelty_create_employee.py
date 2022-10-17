# Copyright 2020-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class NoveltyCreateEmployee(models.TransientModel):
    _name = 'novelty.create.employee'
    _description = 'Novelty Create Employee'

    work_email = fields.Char()
    department_id = fields.Many2one('hr.department', 'Department')
    job_id = fields.Many2one('hr.job', 'Job Position')
    macro_area_id = fields.Many2one('macro.area', 'Macro Area')
    work_group_id = fields.Many2one('work.group', 'Work Group')
    function_executed_id = fields.Many2one(
        'function.executed', 'Function Executed')
    parent_id = fields.Many2one('hr.employee', 'Manager')
    country_id = fields.Many2one('res.country', 'Nationality (Country)')
    bank_account_id = fields.Many2one(
        'res.partner.bank', 'Bank Account Number')
    birthday = fields.Date('Date of Birth')
    country_of_birth = fields.Many2one('res.country', 'Country of Birth')
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
    found_layoffs_id = fields.Many2one(
        'res.partner', 'Found Layoffs',
        domain="[('is_found_layoffs', '=', True)]")
    eps_id = fields.Many2one(
        'res.partner', 'EPS',
        domain="[('is_eps', '=', True)]")
    pension_fund_id = fields.Many2one(
        'res.partner', 'Pension Fund', domain="[('is_afp', '=', True)]")
    unemployment_fund_id = fields.Many2one(
        'res.partner', 'Unemployment Fund',
        domain="[('is_unemployee_fund', '=', True)]")
    arl_id = fields.Many2one(
        'res.partner', 'ARL',
        domain="[('is_arl', '=', True)]")
    prepaid_medicine_id = fields.Many2one(
        'res.partner', 'Prepaid Medicine',
        domain="[('is_prepaid_medicine', '=', True)]")
    prepaid_medicine2_id = fields.Many2one(
        'res.partner', 'Prepaid Medicine 2',
        domain="[('is_prepaid_medicine', '=', True)]")
    afc_id = fields.Many2one(
        'res.partner', 'AFC',
        domain="[('is_afc', '=', True)]")
    voluntary_contribution_id = fields.Many2one(
        'res.partner', 'Voluntary Contribution',
        domain="[('is_voluntary_contribution', '=', True)]")
    address_id = fields.Many2one(
        'res.partner', 'Work Address',
        default=lambda self: self.env.user.company_id.partner_id)
    job_title = fields.Char()

    @api.onchange('job_id')
    def onchange_job_id(self):
        """Fill Job."""
        if self.job_id and self.job_id.name:
            self.job_title = self.job_id.name

    @api.multi
    def confirm(self):
        """Create Employee."""
        active_id = self.env.context.get('active_id')
        novelty_id = self.env['hr.novelty'].browse(active_id)
        if novelty_id.contact_id:
            employee = self.env['hr.employee'].create({
                'name': novelty_id.contact_id.name,
                'work_email': self.work_email,
                'department_id': self.department_id.id,
                'job_id': self.job_id.id,
                'macro_area_id': self.macro_area_id.id,
                'work_group_id': self.work_group_id.id,
                'function_executed_id': self.function_executed_id.id,
                'parent_id': self.parent_id.id,
                'country_id': self.country_id.id,
                'bank_account_id': self.bank_account_id.id,
                'birthday': self.birthday,
                'country_of_birth': self.country_of_birth.id,
                'state_of_birth_id': self.state_of_birth_id.id,
                'place_of_birth_id': self.place_of_birth_id.id,
                'found_layoffs_id': self.found_layoffs_id.id,
                'eps_id': self.eps_id.id,
                'pension_fund_id': self.pension_fund_id.id,
                'unemployment_fund_id': self.unemployment_fund_id.id,
                'arl_id': self.arl_id.id,
                'prepaid_medicine_id': self.prepaid_medicine_id.id,
                'prepaid_medicine2_id': self.prepaid_medicine2_id.id,
                'afc_id': self.afc_id.id,
                'voluntary_contribution_id': self.voluntary_contribution_id.id,
                'address_id': self.address_id.id,
                'job_title': self.job_title,
                'address_home_id': novelty_id.contact_id.id,
            })
            novelty_id.write({
                'employee_id': employee.id})
