# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, Warning
from odoo.addons import decimal_precision as dp


class HrSalaryRule(models.Model):
    _name = 'hr.salary.rule'
    _inherit = ['hr.salary.rule', 'portal.mixin',
                'mail.thread', 'mail.activity.mixin']

    fixed = fields.Boolean(
        help="is this rule fixed (it can't be modified)",
        track_visibility="always")
    account_debit = fields.Many2one(
        'account.account', 'Debit Account',
        domain=[('deprecated', '=', False),
                ('is_payroll', '=', True)],
        track_visibility="always")
    account_credit = fields.Many2one(
        'account.account', 'Credit Account',
        domain=[('deprecated', '=', False),
                ('is_payroll', '=', True)],
        track_visibility="always")
    is_flex = fields.Boolean('Flex', track_visibility="always")
    autocomplete_flex = fields.Boolean(copy=False, track_visibility="always")
    accumulate = fields.Boolean('Accumulate', track_visibility="always")
    print_payslip = fields.Boolean(copy=False, track_visibility="always")
    total_cost = fields.Boolean('Total Cost', track_visibility="always")
    projection_exempt = fields.Boolean(
        'Projection Exempt', track_visibility="always")
    prepaid_medicine_id = fields.Many2one(
        'res.partner', 'Prepaid Medicine',
        domain="[('is_prepaid_medicine', '=', True)]",
        track_visibility="always")
    work_days_value = fields.Char(track_visibility="always")
    calculate_base = fields.Boolean(track_visibility="always")
    asigned_base = fields.Selection([
        ('model', 'Model'),
        ('value', 'Value'),
        ('categ', 'Categ')], default='model', track_visibility="always")
    value = fields.Char(track_visibility="always")
    categ = fields.Char(track_visibility="always")
    model = fields.Many2one('ir.model', track_visibility="always")
    field = fields.Many2one(
        'ir.model.fields', domain="[('model_id', '=', model)]",
        track_visibility="always")
    # Overwrite fields for track visibility Task:- Nomina 367
    name = fields.Char(required=True, translate=True,
                       track_visibility="always")
    code = fields.Char(
        required=True,
        help="The code of salary rules can be used as reference in "
        "computation of other rules. "
        "In that case, it is case sensitive.",
        track_visibility="always")
    sequence = fields.Integer(
        required=True, index=True, default=5, track_visibility="always",
        help='Use to arrange calculation sequence')
    quantity = fields.Char(
        default='1.0', track_visibility="always",
        help="It is used in computation for percentage and fixed amount. "
        "For e.g. A rule for Meal Voucher having fixed amount of "
        u"1€ per worked day can have its quantity defined in expression "
        "like worked_days.WORK100.number_of_days.")
    category_id = fields.Many2one(
        'hr.salary.rule.category', string='Category', required=True,
        track_visibility="always")
    active = fields.Boolean(
        default=True,
        help="If the active field is set to false, it will allow you "
        "to hide the salary rule without removing it.",
        track_visibility="always")
    appears_on_payslip = fields.Boolean(
        string='Appears on Payslip', default=True,
        help="Used to display the salary rule on payslip.",
        track_visibility="always")
    parent_rule_id = fields.Many2one(
        'hr.salary.rule', string='Parent Salary Rule', index=True,
        track_visibility="always")
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env['res.company']._company_default_get(),
        track_visibility="always")
    condition_select = fields.Selection([
        ('none', 'Always True'),
        ('range', 'Range'),
        ('python', 'Python Expression')
    ], string="Condition Based on", default='none', required=True,
        track_visibility="always")
    condition_range = fields.Char(
        string='Range Based on', default='contract.wage',
        help='This will be used to compute the % fields values; in general '
        'it is on basic, but you can also use categories code fields '
        'in lowercase as a variable names (hra, ma, lta, etc.) and the '
        'variable basic.', track_visibility="always")
    condition_python = fields.Text(
        string='Python Condition', required=True, track_visibility="always",
        default='''
                    # Available variables:
                    #----------------------
                    # payslip: object containing the payslips
                    # employee: hr.employee object
                    # contract: hr.contract object
                    # rules: object containing the rules code
                    # (previously computed)
                    # categories: object containing the computed salary
                    # rule categories (sum of amount of all rules belonging
                    # to that category).
                    # worked_days: object containing the computed worked days
                    # inputs: object containing the computed inputs

                    # Note: returned value have to be set in the variable
                    # 'result'

                    result = rules.NET > categories.NET * 0.10''',
        help='Applied this rule for calculation if condition is true. '
        'You can specify condition like basic > 1000.')
    condition_range_min = fields.Float(
        string='Minimum Range',
        help="The minimum amount, applied for this rule.",
        track_visibility="always")
    condition_range_max = fields.Float(
        string='Maximum Range',
        help="The maximum amount, applied for this rule.",
        track_visibility="always")
    amount_select = fields.Selection([
        ('percentage', 'Percentage (%)'),
        ('fix', 'Fixed Amount'),
        ('code', 'Python Code'),
    ], string='Amount Type', index=True, required=True,
        default='fix', help="The computation method for the rule amount.",
        track_visibility="always")
    amount_fix = fields.Float(
        string='Fixed Amount',
        digits=dp.get_precision('Payroll'), track_visibility="always")
    amount_percentage = fields.Float(
        string='Percentage (%)', digits=dp.get_precision('Payroll Rate'),
        help='For example, enter 50.0 to apply a percentage of 50%',
        track_visibility="always")
    amount_python_compute = fields.Text(string='Python Code',
                                        default='''
                    # Available variables:
                    #----------------------
                    # payslip: object containing the payslips
                    # employee: hr.employee object
                    # contract: hr.contract object
                    # rules: object containing the rules code
                    # (previously computed)
                    # categories: object containing the computed
                    # salary rule categories (sum of amount of all rules
                    # belonging to that category).
                    # worked_days: object containing the computed worked days.
                    # inputs: object containing the computed inputs.

                    # Note: returned value have to be set in the variable
                    # 'result'

                    result = contract.wage * 0.10''',
                                        track_visibility="always")
    amount_percentage_base = fields.Char(
        string='Percentage based on',
        help='result will be affected to a variable',
        track_visibility="always")
    register_id = fields.Many2one(
        'hr.contribution.register', string='Contribution Register',
        help="Eventual third party involved in the "
        "salary payment of the employees.",
        track_visibility="always")
    note = fields.Text(string='Description', track_visibility="always")
    analytic_account_id = fields.Many2one(
        'account.analytic.account', 'Analytic Account',
        track_visibility="always")
    account_tax_id = fields.Many2one(
        'account.tax', 'Tax', track_visibility="always")
    account_debit = fields.Many2one(
        'account.account', 'Debit Account',
        domain=[('deprecated', '=', False)], track_visibility="always")
    account_credit = fields.Many2one(
        'account.account', 'Credit Account',
        domain=[('deprecated', '=', False)], track_visibility="always")

    @api.multi
    def copy(self, default=None):
        """Sequence and Name while copy."""
        self.ensure_one()
        sequence = 1
        salary_rule_seq = self.env['hr.salary.rule'].search_read(
            [('sequence', '!=', False)], ['sequence'],
            order='sequence desc', limit=1)
        if salary_rule_seq:
            sequence = salary_rule_seq[0].get('sequence', '') + 1
        default = dict(default or {}, name=_(
            '%s (copy)') % self.name, sequence=sequence)
        return super(HrSalaryRule, self).copy(default)

    @api.constrains('autocomplete_flex')
    def _check_autocomplete_flex(self):
        if self.search_count([('autocomplete_flex', '=', True)]) > 1:
            raise ValidationError(_(
                "Autocomplete Flex already exist in the another record."))

    @api.multi
    @api.constrains('name')
    def check_data(self):
        """No Duplication."""
        for rec in self:
            if rec.name and \
                    len(self.env['hr.salary.rule'].search(
                        [('name', '=', rec.name),
                         ('code', '=', rec.code)])) > 1:
                raise ValidationError(
                    _("Salary Rule (%s) (%s) already exist!.") % (
                        rec.name, rec.code))


class HrPayrollStructure(models.Model):
    _inherit = "hr.payroll.structure"

    type_id = fields.Many2one('hr.payroll.structure.type', string='Type')

    @api.model
    def create(self, vals):
        res = super(HrPayrollStructure, self).create(vals)
        if res.parent_id and res.rule_ids:
            res.check_duplicate_hr_rule()
        return res

    @api.multi
    def write(self, vals):
        res = super(HrPayrollStructure, self).write(vals)
        if self.parent_id and self.rule_ids:
            self.check_duplicate_hr_rule()
        return res

    @api.multi
    def check_duplicate_hr_rule(self):
        if self.parent_id and self.rule_ids:
            duplicate_ids = list(
                set(self.parent_id.rule_ids) & set(self.rule_ids))
            duplicate_rule_name_list = [
                hr_rule_id.name for hr_rule_id in duplicate_ids]
            if duplicate_rule_name_list:
                raise Warning(_("Following salary rule is duplicate either"
                                " in Salary Rules or Parent Salary Rules!"
                                "\n %s") % duplicate_rule_name_list)


class HrPayrollStructureType(models.Model):
    _name = "hr.payroll.structure.type"
    _description = 'HR Payroll Structure Type'

    name = fields.Char(required=True)
    description = fields.Text()
