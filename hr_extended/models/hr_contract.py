# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class HrEmployee(models.Model):
    _inherit = 'hr.contract'

    agency_id = fields.Many2one('res.partner', 'Agency',
                                track_visibility='onchange')
    parent_company_id = fields.Many2one('res.partner', 'Parent Company',
                                 track_visibility='onchange')
    exclude_from_seniority = fields.Boolean(
        help="Check this box if the contract "
             "is not included for the seniority calculation",
        track_visibility='onchange')
    fix_wage_amount = fields.Float(
        'Fix Wage Amount', track_visibility='onchange')
    fix_wage_perc = fields.Float('Fix Wage Percentage',
                                 compute='_compute_fix_wage_perc',
                                 store=True,
                                 track_visibility='onchange', digits=(3, 2))
    flex_wage_amount = fields.Float('Flex Wage Amount',
                                    compute='_compute_flex_wage_amount',
                                    store=True,
                                    track_visibility='onchange')
    flex_wage_perc = fields.Float('Flex Wage Percentage',
                                  compute='_compute_flex_wage_perc',
                                  store=True,
                                  track_visibility='onchange', digits=(3, 2))
    total_perc = fields.Float('Total Percentage',
                              compute='_compute_total_percentage',
                              store=True,
                              track_visibility='onchange', digits=(3, 2))
    flex_wage_ids = fields.One2many(
        'hr.contract.flex_wage',
        'contract_id',
        string="Detailed Flex Wage",
        copy=True)
    date_end_required = fields.Boolean(related='type_id.date_end_required',
                                       track_visibility='onchange')
    arl_percentage = fields.Float('ARL Percentage', digits=(32, 6))
    compare_amount = fields.Float('Compare Amount(%)')

    @api.onchange('fix_wage_amount')
    def onchange_fix_wage_amount(self):
        if self.wage > 0 and self.fix_wage_amount > 0 and\
                self.wage > self.fix_wage_amount:
            if self.flex_wage_ids:
                self.flex_wage_ids[0].amount = self.wage - self.fix_wage_amount
            else:
                salary_rule_id = ''
                if self.struct_id.type_id.name == 'Nuevo Flex':
                    salary_rule_id = self.env['hr.salary.rule'].search(
                        [('autocomplete_flex', '=', True)], limit=1).id
                self.flex_wage_ids = [
                    (0, 0,
                     {'salary_rule_id': salary_rule_id,
                      'amount': self.wage - self.fix_wage_amount}
                     )]
        if self.fix_wage_perc and self.fix_wage_perc < 60.0:
            return {
                'warning': {
                    'title': "Warning", 'message':
                    _("By law, the fixed salary can not be less than 60 "
                      "percent of the total salary.")},
            }

    @api.multi
    def set_entry_date(self, contarct_id):
        """ get the entry date from the first contract start date """
        contract = self.env['hr.contract']
        domain = [
             ('employee_id', '=', self.employee_id.id),
             ('exclude_from_seniority', '=', False)]
        if contarct_id:
            domain += [('id', 'not in', contarct_id.ids)]
        contract_id = contract.search(domain, order='date_start asc', limit=1)
        if self.employee_id:
            self.employee_id.entry_date = contract_id.date_start

    @api.model
    def create(self, vals):
        res = super(HrEmployee, self).create(vals)
        if vals.get('date_start'):
            res.set_entry_date([])
        return res

    """@api.model
    def write(self, vals):
        if vals.get('wage', ''):
            vals.update({'compare_amount': (float(vals.get('wage', '1.0') * 100 / self.wage) - 100)})
        res = super(HrEmployee, self).write(vals)
        if vals.get('date_start') or vals.get('employee_id'):
            self.set_entry_date([])
        return res """

    @api.multi
    def unlink(self):
        for record in self:
            record.set_entry_date(record)
        return super(HrEmployee, self).unlink()

    @api.constrains('flex_wage_perc')
    def _check_flex_wage_perc(self):
        for rec in self:
            if rec.flex_wage_perc and (
                    rec.flex_wage_perc < 0.0 or rec.flex_wage_perc > 100.0):
                raise ValidationError(
                    _('Flex Wage Percentage must be between 0 and 100.'))

    @api.depends('wage', 'fix_wage_amount')
    def _compute_fix_wage_perc(self):
        for rec in self.filtered('wage'):
            rec.fix_wage_perc = round(rec.fix_wage_amount / rec.wage * 100, 2)

    @api.depends('flex_wage_ids.amount')
    def _compute_flex_wage_amount(self):
        for rec in self:
            rec.flex_wage_amount = sum(rec.flex_wage_ids.mapped('amount'))

    @api.onchange('flex_wage_ids')
    def _compute_flex_wage_ids_percentage(self):

        if self.flex_wage_amount:
            for flex in self.flex_wage_ids:
                flex.percentage = flex.amount / self.flex_wage_amount * 100

    @api.depends('wage', 'flex_wage_amount')
    def _compute_flex_wage_perc(self):
        for rec in self.filtered('wage'):
            rec.flex_wage_perc = round(rec.flex_wage_amount / rec.wage * 100, 2)

    @api.depends('fix_wage_perc', 'flex_wage_perc')
    def _compute_total_percentage(self):
        for rec in self:
            rec.total_perc = rec.fix_wage_perc + rec.flex_wage_perc

    @api.constrains('total_perc')
    def _check_total_perc(self):
        for rec in self:
            if rec.total_perc and (rec.total_perc != 100.0) and not rec._context.get('from_novelty', ''):
                raise ValidationError(_(
                    "Total percentage must be 100.00."))

    @api.multi
    def send_contract_ending_notification(self, days=45):
        ending_date = fields.Date.today() + relativedelta(days=days)
        contract_ids = self.search([('state', 'in', ['open']),
                                    ('date_end', '<', ending_date)])

        for contract in contract_ids:
            mail_list = "%s, " % (contract.employee_id.parent_id.work_email)

            # ToDo: Send to payroll manager and BPs

            values = {
                'email_to': mail_list,
            }

            mail_template_id = self.env.ref(
                'hr_extended.email_template_contract_ending_notification')
            mail_template_id.send_mail(contract.id, email_values=values)


class HrContractType(models.Model):
    _inherit = 'hr.contract.type'

    date_end_required = fields.Boolean()
    description = fields.Text()


class HrContractFlexWage(models.Model):
    _name = 'hr.contract.flex_wage'
    _description = 'Flex Wage Detailed List'
    _inherit = 'mail.thread'

    salary_rule_id = fields.Many2one(
        'hr.salary.rule',
        domain=[('is_flex', '=', True)],
        track_visibility='onchange')
    fixed = fields.Boolean(related='salary_rule_id.fixed',
                           track_visibility='onchange')
    amount = fields.Float(track_visibility='onchange')
    percentage = fields.Float(track_visibility='onchange', digits=(3, 2))
    contract_id = fields.Many2one('hr.contract',
                                  track_visibility='onchange')
    description = fields.Text()
