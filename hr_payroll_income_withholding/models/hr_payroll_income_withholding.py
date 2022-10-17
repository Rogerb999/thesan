# -*- coding: utf-8 -*-

import datetime
from odoo import api, fields, models


class HrDeductionsTypeRF(models.Model):
    _name = 'hr.deduction.type.rf'
    _description = 'Deduction Type'
    _inherit = [
        'mail.thread', 'mail.activity.mixin'
    ]

    @api.multi
    def _check_state(self):
        date = fields.Date.today()
        hr_deduction_type_rf_ids = self.search([
            ('active', '=', 'True'),
            ('end_date', '<', date)
        ])
        for hr_deduction_type_rf_id in hr_deduction_type_rf_ids:
            hr_deduction_type_rf_id.write({
                'date_inactive': date,
                'active': False
            })

    name = fields.Char(required=True)
    description = fields.Text()
    sequence = fields.Integer(string='Sequence', required=True)
    active = fields.Boolean(string='Active', default=True)
    date_inactive = fields.Date(string="Date Inactive", readonly=True)
    end_date = fields.Date(string="End Date")
    max_uvt = fields.Float()
    max_value = fields.Float()
    max_acumulate = fields.Float()


class HrDeductionRF(models.Model):
    _name = 'hr.deduction.rf'
    _description = 'Deduction'
    _inherit = [
        'mail.thread', 'mail.activity.mixin'
    ]

    name = fields.Char(required=True)
    type_id = fields.Many2one('hr.deduction.type.rf', string="Type")
    max_uvt = fields.Float(string="Maximum UVT")
    max_percentage = fields.Float(string="Maximum Percentage")
    max_value = fields.Float(string="Maximum Value")
    max_acumulate = fields.Float(string="Maximum Acumulate")
    description = fields.Text()
    active = fields.Boolean(
        string='Active', default=True,
        help="If its checked, indicates that is active for date.")
    dependent = fields.Boolean(string='Dependent')


class HrDeductionsRFEmployee(models.Model):
    _name = 'hr.deductions.rf.employee'
    _description = 'Deductions Employee'
    _inherit = [
        'mail.thread', 'mail.activity.mixin'
    ]
    _order = 'value'

    @api.model
    def _check_state(self):
        date = fields.Date.today()
        hr_deduction_type_rf_employee_ids = self.search([
            ('active', '=', 'True'),
            ('date_end', '<', date)
        ])
        for hr_deduction_type_rf_employee_id in\
                hr_deduction_type_rf_employee_ids:
            hr_deduction_type_rf_employee_id.write({
                'active': False
            })

    name = fields.Char(required=True)
    hr_deduction_type_id = fields.Many2one(
        'hr.deduction.type.rf', string="Type", required="True")
    hr_deduction_id = fields.Many2one(
        'hr.deduction.rf', string="Deduction", required="True")
    value = fields.Float(string="Value", required="True")
    employee_id = fields.Many2one('hr.employee', string="Employee")
    active = fields.Boolean(string='Active', default=True)
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    date_end = fields.Date()
    obtain_plines = fields.Boolean(string='Obtail value line payslip')
    rule_id = fields.Many2one(
        'hr.salary.rule', string="Rule")
    description = fields.Text()

    @api.onchange('date_end')
    def onchange_date_end(self):
        if self.date_end:
            if self.date_end < fields.Date.today():
                self.active = False
            else:
                self.active = True

    @api.onchange('hr_deduction_type_id')
    def onchange_hr_deduction_type_id(self):
        self.hr_deduction_id = ''


class HrRetentionMethod(models.Model):
    _name = 'hr.retention.method.rf'
    _description = 'Retention Method'
    _inherit = [
        'mail.thread', 'mail.activity.mixin'
    ]

    name = fields.Char(required=True)
    description = fields.Text()


class HrDeductionAccumulateRetention(models.Model):
    _name = 'hr.deduction.accumulate.rf'
    _description = 'Deduction Accumulate'
    _inherit = [
        'mail.thread', 'mail.activity.mixin'
    ]

    name = fields.Char(required=True)
    year = fields.Integer(string="Year")
    employee_id = fields.Many2one('hr.employee', string="Employee")
    accumulate = fields.Float(string="Accumulate Deduction")


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    retention_method_id = fields.Many2one(
        'hr.retention.method.rf', string="Retention Method",
        track_visibility='onchange')
    withholding_2 = fields.Float('Retention Method 2', digits=(32, 6),
                                 track_visibility='onchange')
    deductions_ids = fields.One2many(
        'hr.deductions.rf.employee', 'employee_id',
        string='Deductions', help="The list of deductions for employee")
    deductions_accumulate_ids = fields.One2many(
        'hr.deduction.accumulate.rf', 'employee_id',
        string='Accumulate Deductions',
        help="The accumulate of deductions for year")
    is_dependientes = fields.Boolean(
        'Dependientes', track_visibility='onchange')

    @api.multi
    def calculate_accumulate(self):
        today = fields.Date.today()
        start_date = datetime.date(today.year, 1, 1)
        end_date = datetime.date(today.year, 12, 31)
        payslip_ids = self.env['hr.payslip'].search(
            [('state', 'in', ['done', 'paid']),
             ('employee_id', '=', self.id),
             ('date_from', '>=', start_date),
             ('date_from', '<=', end_date),
             ])
        total_accumulate = 0
        for payslip_id in payslip_ids:
            for ded_id in payslip_id.ps_renting_additional_ids:
                total_accumulate += ded_id.value_final

        hr_deduction_type_id = self.env['hr.deduction.accumulate.rf'].search(
            [('year', '=', str(today.year)),
             ('employee_id', '=', self.id),
             ])
        if not hr_deduction_type_id:
            self.env['hr.deduction.accumulate.rf'].create(
                {'name': self.name + str(today.year),
                 'year': str(today.year),
                 'employee_id': self.id,
                 'accumulate': total_accumulate,
                 })
        return True

    @api.onchange('is_dependientes')
    def onchange_is_dependientes(self):
        value = 0.0
        if self.is_dependientes:
            hr_deduction_id = self.env['hr.deduction.rf'].search(
                [('dependent', '=', True)], limit=1)
            contract = self.env['hr.contract'].search(
                [('state', '=', 'open'),
                 ('employee_id', '=', self._origin.id)],
                limit=1)
            if not contract:
                contract = self.env['hr.contract'].search(
                    [('state', 'not in', ['close', 'cancel']),
                     ('employee_id', '=', self._origin.id)],
                    limit=1)
            if contract and ((
                    contract.wage * 10) / 100) < hr_deduction_id.max_value:
                value = (contract.wage * 10) / 100
            else:
                value = hr_deduction_id.max_value
            deductions_ids = self.env['hr.deductions.rf.employee'].search(
                [('employee_id', '=', self._origin.id)])
            if hr_deduction_id:
                deduction_id = self.env['hr.deductions.rf.employee'].create({
                    'name': 'DEDUCCIONES DEPENDIENTES',
                    'hr_deduction_type_id': hr_deduction_id.type_id.id,
                    'hr_deduction_id': hr_deduction_id.id,
                    'value': value
                })
            deductions_ids = self.env['hr.deductions.rf.employee'].search(
                [('employee_id', '=', self._origin.id)])
            if deduction_id:
                listded = deductions_ids.ids + [deduction_id.id]
            else:
                listded = deductions_ids.ids
            return {'value': {'deductions_ids': listded}}


class HrUVTValueRangeRF(models.Model):
    _name = "hr.value.uvt.range.rf"
    _description = 'Range calculate UVT'
    _order = "value_uvt_max"
    _inherit = [
        'mail.thread', 'mail.activity.mixin'
    ]

    value_uvt_max = fields.Integer(
        string="Value UVT Max", required=True, track_visibility='always')
    uvt_discount = fields.Integer(
        string="UVT Discount", required=True, track_visibility='always')
    marginal_rate = fields.Float(
        string="Marginal Rate", required=True, track_visibility='always')
    uvt_additional = fields.Integer(
        string="UVT Additional", required=True, track_visibility='always')
    description = fields.Text(track_visibility='always')
    hr_uvtvalue_id = fields.Many2one(
        'hr.value.uvt.rf', string="Value UVT", required="True",
        track_visibility='always')


class HrUVTValueInputNotRF(models.Model):
    _name = "hr.value.uvt.input.not.rf"
    _description = 'Input Not RF'
    _inherit = [
        'mail.thread', 'mail.activity.mixin'
    ]

    name = fields.Char(
        required=True, track_visibility='always')
    rule_id = fields.Many2one(
        'hr.salary.rule', string="Rule", required="True",
        track_visibility='always')
    sequence = fields.Integer(
        string="Sequence", track_visibility='always')
    hr_uvtvalue_id = fields.Many2one(
        'hr.value.uvt.rf', string="Value UVT", required="True",
        track_visibility='always')


class HrUVTValueInputRF(models.Model):
    _name = "hr.value.uvt.input.rf"
    _description = 'Input RF'
    _inherit = [
        'mail.thread', 'mail.activity.mixin'
    ]

    name = fields.Char(
        required=True, track_visibility='always')
    rule_id = fields.Many2one(
        'hr.salary.rule', string="Rule", required="True",
        track_visibility='always')
    sequence = fields.Integer(
        string="Sequence", track_visibility='always')
    hr_uvtvalue_id = fields.Many2one(
        'hr.value.uvt.rf', string="Value UVT", required="True",
        track_visibility='always')
    exempt_rm_id = fields.Many2one(
        'hr.retention.method.rf', string="Exempt retention Method",
        track_visibility='always')


class HrUVTValueRF(models.Model):
    _name = "hr.value.uvt.rf"
    _description = 'Value UVT'
    _inherit = [
        'mail.thread', 'mail.activity.mixin'
    ]

    name = fields.Char(required=True, track_visibility='always')
    value = fields.Float(
        string="Value", required=True, track_visibility='always')
    start_date = fields.Date(
        string="Start Date", required=True, track_visibility='always')
    end_date = fields.Date(
        string="End Date", required=True, track_visibility='always')
    status = fields.Boolean(
        string='Active',
        help="If its checked, indicates that is active for date.",
        track_visibility='always')
    percentage_renting_exempt = fields.Float(
        string="Percentage Rent Excent", required=True,
        track_visibility='always')
    max_value_renting_exempt = fields.Float(
        string="Maximun Value Rent Excent", required=True,
        track_visibility='always')
    max_uvt_deduction_renting_exempt = fields.Float(
        string="Maximun UVT Deduction Renting Exempt",
        track_visibility='always')
    percentage_max_deduction = fields.Float(
        string="Percentage Maximun Deduction",
        track_visibility='always')
    range_retention_ids = fields.One2many(
        'hr.value.uvt.range.rf', 'hr_uvtvalue_id', string='Range UVT Value',
        shelp="The list of range UVT")
    rule_ids = fields.One2many(
        'hr.value.uvt.input.not.rf', 'hr_uvtvalue_id',
        string='Rules Input Not RF',
        shelp="The list of range UVT")
    irf_rule_ids = fields.One2many(
        'hr.value.uvt.input.rf', 'hr_uvtvalue_id', string='Rules Input RF',
        shelp="The list of range UVT")

    @api.model
    def create(self, vals):
        if vals['status'] is True:
            uvt_id = self.env['hr.value.uvt.rf'].search([
                ('status', '=', True)])
            uvt_id.write({'status': False})
        return super(HrUVTValueRF, self).create(vals)


class HrSalaryRule(models.Model):
    _inherit = "hr.salary.rule"

    code_sara = fields.Char(string="Code Sara", track_visibility="always")


class HrPayslipDeductionsRF(models.Model):
    _name = "hr.payslip.deductions.rf"
    _description = 'Payslip Deductions RF'
    _order = "sequence"
    _inherit = [
        'mail.thread', 'mail.activity.mixin'
    ]

    @api.model
    def create(self, vals):
        if self._context.get('transfer_data', '') and not vals.get(
                'hr_payslip_id', '') or not vals.get(
                    'hr_deductions_rf_employee_id', '') or not vals.get(
                        'value_reference', '') or not vals.get(
                            'value_final', ''):
            return False
        return super(HrPayslipDeductionsRF, self).create(vals)

    hr_deductions_rf_employee_id = fields.Many2one(
        'hr.deductions.rf.employee', string="Deductions", required="True")
    hr_deduction_type_id = fields.Many2one(
        related="hr_deductions_rf_employee_id.hr_deduction_type_id")
    sequence = fields.Integer(string="Sequence")
    value_reference = fields.Float(string="Value Reference", required=True)
    value_final = fields.Float(string="Value final", required=True)
    hr_payslip_id = fields.Many2one(
        'hr.payslip', string="Payslip", required="True")
    description = fields.Text()


class HrPayslipInputNotRF(models.Model):
    _name = "hr.payslip.input.not.rf"
    _description = 'Payslip Input Not RF'
    _order = "sequence"
    _inherit = [
        'mail.thread', 'mail.activity.mixin'
    ]

    @api.model
    def create(self, vals):
        if self._context.get('transfer_data', '') and not vals.get(
                'hr_payslip_id', '') or not vals.get('value_final', ''):
            return False
        return super(HrPayslipInputNotRF, self).create(vals)

    name = fields.Char(required=True)
    rule_id = fields.Many2one('hr.salary.rule', string="Rule", required="True")
    sequence = fields.Integer(string="Sequence")
    value_final = fields.Float(string="Value final", required=True)
    hr_payslip_id = fields.Many2one(
        'hr.payslip', string="Payslip", required="True")
    description = fields.Text()


class HrPayslipInputRF(models.Model):
    _name = "hr.payslip.input.rf"
    _description = 'Payslip Input RF'
    _order = "sequence"
    _inherit = [
        'mail.thread', 'mail.activity.mixin'
    ]

    @api.model
    def create(self, vals):
        if self._context.get('transfer_data', '') and not vals.get(
                'hr_payslip_id', '') or not vals.get('value_final', ''):
            return False
        return super(HrPayslipInputRF, self).create(vals)

    name = fields.Char(required=True)
    rule_id = fields.Many2one('hr.salary.rule', string="Rule", required="True")
    sequence = fields.Integer(string="Sequence")
    value_final = fields.Float(string="Value final", required=True)
    hr_payslip_id = fields.Many2one(
        'hr.payslip', string="Payslip", required="True")
    description = fields.Text()


class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    ps_input_rf_ids = fields.One2many(
        'hr.payslip.input.rf', 'hr_payslip_id',
        string='Input RF',
        help="The list of Inputs rf for employee")
    ps_input_no_rf_ids = fields.One2many(
        'hr.payslip.input.not.rf', 'hr_payslip_id',
        string='Input no RF',
        help="The list of Inputs not rf for employee")
    ps_deductions_ids = fields.One2many(
        'hr.payslip.deductions.rf', 'hr_payslip_id',
        string='Deductions',
        help="The list of deductions for employee",
        domain=[('sequence', '=', 2)])
    ps_renting_additional_ids = fields.One2many(
        'hr.payslip.deductions.rf', 'hr_payslip_id',
        string='Renting Additional',
        help="The list of deductions for employee",
        domain=[('sequence', '=', 3)])
    ps_exempt_income_ids = fields.One2many(
        'hr.payslip.deductions.rf', 'hr_payslip_id',
        string='Exempt Income',
        help="The list of exempt income",
        domain=[('sequence', '=', 4)])
    calculate_renting_exempt = fields.Float(
        string="calculate renting exempt renting",
        compute='_compute_calculate_renting_exempt',
        store=True)
    calculate_renting_exempt_cont = fields.Float(
        string="calculate renting exempt renting Contingente",
        compute='_compute_calculate_renting_exempt_cont',
        store=True)
    sum_input_no_rf = fields.Float(compute='_calculate_sum_input_no_rf')
    inputs_rent = fields.Float(
        string="Inputs Rent",
        compute='_compute_inputs_rent',
        store=True)
    subtotal_1 = fields.Float(
        string="Subtotal 1",
        compute='_compute_subtotal_1',
        store=True)
    sum_deductions = fields.Float(compute='_calculate_deductions')
    subtotal_2 = fields.Float(
        string="Subtotal 2",
        compute='_compute_subtotal_2',
        store=True)
    sum_rent_add = fields.Float(compute='_calculate_rent_add')
    total_renting_excempt = fields.Float(
        string="Total renting excempt",
        compute='_compute_total_renting_excempt',
        store=True)
    subtotal_3 = fields.Float(
        string="Subtotal 3",
        compute='_compute_subtotal_3',
        store=True)
    subtotal_3_cont = fields.Float(
        string="Subtotal 3 Cont",
        compute='_compute_subtotal_3_cont',
        store=True)
    subtotal_4 = fields.Float(
        string="Subtotal 4",
        compute='_compute_subtotal_4',
        store=True)
    subtotal_4_cont = fields.Float(
        string="Subtotal 4 Contigente",
        compute='_compute_subtotal_4_cont',
        store=True)
    total_deductions_renting = fields.Float(
        string="Total Deductions and exempt renting",
        compute='_compute_total_deductions_renting',
        store=True)
    total_deductions_renting_cont = fields.Float(
        string="Total Deductions and exempt renting Contingente",
        compute='_compute_total_deductions_renting_cont',
        store=True)
    total_base_retention = fields.Float(
        compute='_calculate_total_base_retention')
    base_income_retention = fields.Float(
        string="Base Income Retention",
        compute='_compute_base_income_retention',
        store=True)
    base_income_retention_cont = fields.Float(
        string="Base Income Retention Cont",
        compute='_compute_base_income_retention_cont',
        store=True)
    income_represented_uvt = fields.Float(
        string="Income Represented UVT",
        compute='_compute_income_represented_uvt',
        store=True)
    income_represented_uvt_cont = fields.Float(
        string="Income Represented UVT Contingente",
        compute='_compute_income_represented_uvt_cont',
        store=True)
    total_retention_income = fields.Float(
        string="Total Retention Income",
        compute='_compute_total_retention_income',
        store=True)
    total_retention_income_cont = fields.Float(
        string="Total Retention Income Contingente",
        compute='_compute_total_retention_income_cont',
        store=True)
    percentage_renting_calculate = fields.Float(
        string="Percentage Renting Calculate", digits=(32, 6))

    @api.depends('ps_input_rf_ids')
    def _compute_inputs_rent(self):
        result = 0
        for reg in self:
            result_days = sum([work_days.number_of_days for work_days
                               in reg.worked_days_line_ids])
            if reg.contract_completion_id and\
                    reg.employee_id.retention_method_id.name == '2':
                for inputs in reg.ps_input_rf_ids:
                    if inputs.rule_id.projection_exempt or result_days == 0:
                        result += inputs.value_final
                    elif result_days < 0: 
                        result += inputs.value_final / 30 * result_days
                        result += inputs.value_final
                    else:
                        result += inputs.value_final / 30 * result_days
                reg.inputs_rent = result
            else:
                for inputs in reg.ps_input_rf_ids:
                    result += inputs.value_final
                reg.inputs_rent = result
        return result

    @api.depends('ps_input_no_rf_ids', 'ps_input_no_rf_ids.value_final',
                 'state')
    def _calculate_sum_input_no_rf(self):
        for rec in self:
            if rec.state == 'draft':
                result = 0.0
                for line in rec.ps_input_no_rf_ids:
                    if line.value_final:
                        result += line.value_final
                rec.sum_input_no_rf = result

    @api.depends('ps_input_rf_ids', 'ps_input_no_rf_ids')
    def _compute_subtotal_1(self):
        for reg in self:
            result = 0
            result_days = sum([work_days.number_of_days for work_days
                               in reg.worked_days_line_ids])
            if reg.contract_completion_id and\
                    reg.employee_id.retention_method_id.name == '2':
                for inputs in reg.ps_input_no_rf_ids:
                    if inputs.rule_id.projection_exempt or result_days == 0:
                        result += inputs.value_final
                    elif result_days < 0:
                        result += inputs.value_final * -1
                    else:
                        result += inputs.value_final / 30 * result_days
                reg.subtotal_1 = reg.inputs_rent + result
            else:
                result = sum([inputs.value_final for inputs
                              in reg.ps_input_no_rf_ids])
                reg.subtotal_1 = reg.inputs_rent + result
        return result

    @api.depends('ps_deductions_ids', 'ps_deductions_ids.value_final', 'state')
    def _calculate_deductions(self):
        for rec in self:
            if rec.state == 'draft':
                result = 0.0
                val_uvt = self.env['hr.value.uvt.rf'].search(
                    [('status', '=', True)])
                for line in rec.ps_deductions_ids:
                    if line.value_final:
                        result += line.value_final
                if val_uvt:
                    percentage_value = rec.subtotal_1 *\
                        val_uvt.percentage_max_deduction / 100
                    if result > percentage_value and\
                            val_uvt.percentage_max_deduction > 0:
                        result = percentage_value
                rec.sum_deductions = result

    @api.depends('ps_deductions_ids', 'subtotal_1')
    def _compute_subtotal_2(self):
        result = 0
        for reg in self:
            reg.subtotal_2 = reg.subtotal_1 - reg.sum_deductions
        return result

    @api.depends('ps_renting_additional_ids',
                 'ps_renting_additional_ids.value_final', 'state')
    def _calculate_rent_add(self):
        for rec in self:
            if rec.state == 'draft':
                result = 0.0
                for line in rec.ps_renting_additional_ids:
                    if line.value_final:
                        result += line.value_final
                rec.deductions = result

    @api.depends('ps_renting_additional_ids', 'subtotal_1', 'subtotal_2')
    def _compute_total_renting_excempt(self):
        result = 0
        accumulate = 0
        accumulate_total = 0
        val_uvt = self.env['hr.value.uvt.rf'].search([('status', '=', True)])
        max_discount = val_uvt.value * val_uvt.max_uvt_deduction_renting_exempt
        accumulate_id = self.env['hr.deduction.accumulate.rf'].search(
            [('year', '=', self.date_to.year),
             ('employee_id', '=', self.employee_id.id)])
        for acc in accumulate_id:
            accumulate = acc.accumulate
        for reg in self:
            result = sum([additionals.value_final for additionals
                          in reg.ps_renting_additional_ids])
            accumulate_total = accumulate + result
            if accumulate > max_discount:
                result = 0
            elif accumulate_total > max_discount:
                result = max_discount - accumulate
            reg.total_renting_excempt = result
        return result

    @api.depends('total_renting_excempt', 'subtotal_1', 'subtotal_2')
    def _compute_subtotal_3(self):
        result = 0
        for reg in self:
            reg.subtotal_3 = reg.subtotal_2 - reg.total_renting_excempt
        return result

    @api.depends('subtotal_1', 'subtotal_2')
    def _compute_subtotal_3_cont(self):
        result = 0
        for reg in self:
            reg.subtotal_3_cont = reg.subtotal_2
        return result

    @api.depends('ps_exempt_income_ids', 'subtotal_1',
                 'subtotal_2', 'subtotal_3')
    def _compute_calculate_renting_exempt(self):
        result = 0
        active_uvt = self.env['hr.value.uvt.rf'].search([
            ('status', '=', True)])
        if not active_uvt:
            return result
        for reg in self:
            result = \
                reg.subtotal_3 * active_uvt.percentage_renting_exempt / 100
            if result > active_uvt.max_value_renting_exempt:
                result = active_uvt.max_value_renting_exempt
            reg.calculate_renting_exempt = result
        return result

    @api.depends('ps_exempt_income_ids', 'subtotal_1',
                 'subtotal_2', 'subtotal_3_cont')
    def _compute_calculate_renting_exempt_cont(self):
        result = 0
        active_uvt = self.env['hr.value.uvt.rf'].search([
            ('status', '=', True)])
        if not active_uvt:
            return result
        for reg in self:
            result = \
                reg.subtotal_3_cont *\
                active_uvt.percentage_renting_exempt / 100
            if result > active_uvt.max_value_renting_exempt:
                result = active_uvt.max_value_renting_exempt
            reg.calculate_renting_exempt_cont = result
        return result

    @api.depends('ps_exempt_income_ids', 'subtotal_1',
                 'subtotal_2', 'subtotal_3', 'calculate_renting_exempt')
    def _compute_subtotal_4(self):
        result = 0
        for reg in self:
            reg.subtotal_4 = reg.subtotal_3 - reg.calculate_renting_exempt
        return result

    @api.depends('ps_exempt_income_ids', 'subtotal_1',
                 'subtotal_2', 'subtotal_3_cont',
                 'calculate_renting_exempt_cont')
    def _compute_subtotal_4_cont(self):
        result = 0
        for reg in self:
            reg.subtotal_4_cont = reg.subtotal_3_cont -\
                reg.calculate_renting_exempt_cont
        return result

    @api.depends('subtotal_1', 'subtotal_2', 'subtotal_3', 'subtotal_4')
    def _compute_total_deductions_renting(self):
        result = 0
        percentage_salary = 0
        val_uvt = self.env['hr.value.uvt.rf'].search([('status', '=', True)])
        if not val_uvt:
            return result
        t_deduction = 0
        for reg in self:
            t_deduction = sum([deductions.value_final for deductions
                               in reg.ps_deductions_ids])
            t_deduction += reg.total_renting_excempt
            t_deduction += reg.calculate_renting_exempt
            result = t_deduction
            percentage_salary = reg.subtotal_1 * 0.40
            if result > percentage_salary:
                result = percentage_salary
            reg.total_deductions_renting = result
        return result

    @api.depends('subtotal_1', 'subtotal_2', 'subtotal_3_cont',
                 'subtotal_4_cont')
    def _compute_total_deductions_renting_cont(self):
        result = 0
        percentage_salary = 0
        val_uvt = self.env['hr.value.uvt.rf'].search([('status', '=', True)])
        if not val_uvt:
            return result
        t_deduction = 0
        for reg in self:
            t_deduction = sum([deductions.value_final for deductions
                               in reg.ps_deductions_ids])
            t_deduction += reg.calculate_renting_exempt_cont
            result = t_deduction
            percentage_salary = reg.subtotal_1 * 0.40
            if result > percentage_salary or result == 0:
                result = percentage_salary
            reg.total_deductions_renting_cont = result
        return result

    @api.depends('subtotal_1', 'total_deductions_renting', 'state')
    def _calculate_total_base_retention(self):
        for rec in self:
            if rec.state == 'draft':
                if rec.subtotal_1 and rec.total_deductions_renting:
                    rec.total_base_retention = rec.subtotal_1 -\
                        rec.total_deductions_renting

    @api.depends('total_deductions_renting')
    def _compute_base_income_retention(self):
        result = 0
        for reg in self:
            result = reg.subtotal_1 - reg.total_deductions_renting
            reg.base_income_retention = result
        return result

    @api.depends('total_deductions_renting_cont')
    def _compute_base_income_retention_cont(self):
        result = 0
        for reg in self:
            result = reg.subtotal_1 - reg.total_deductions_renting_cont
            reg.base_income_retention_cont = result
        return result

    @api.depends('base_income_retention')
    def _compute_income_represented_uvt(self):
        result = 0
        for reg in self:
            val_uvt = self.env['hr.value.uvt.rf'].search(
                [('status', '=', True)])
            if val_uvt:
                if reg.employee_id.retention_method_id.name == '1':
                    if reg.base_income_retention != 0:
                        result = reg.base_income_retention / val_uvt.value
                        reg.income_represented_uvt = result
            else:
                reg.income_represented_uvt = result
        return result

    @api.depends('base_income_retention_cont')
    def _compute_income_represented_uvt_cont(self):
        result = 0
        for reg in self:
            val_uvt = self.env['hr.value.uvt.rf'].search(
                [('status', '=', True)])
            if val_uvt:
                if reg.employee_id.retention_method_id.name == '1':
                    if reg.base_income_retention_cont != 0:
                        result = reg.base_income_retention_cont / val_uvt.value
                        reg.income_represented_uvt_cont = result
            else:
                reg.income_represented_uvt_cont = result
        return result

    @api.depends('income_represented_uvt', 'base_income_retention','description')
    def _compute_total_retention_income(self):
        result = 0
        for reg in self:
            leave_type_ids = self.env['hr.leave.type'].search(
                [('no_count_rent', '=', True)])
            list_leave = ()
            list_leaves = ''
            for lt_id in leave_type_ids:
                list_leaves += lt_id.name
            list_leave = (list_leaves)
            result_days = sum([work_days.number_of_days for work_days
                               in reg.worked_days_line_ids if
                               work_days.name not in list_leave])
            days0 = False
            basic_days = 30
            if result_days > 30:
                basic_days = result_days
            if result_days == 0:
                days0 = True
                result_days = 30
            uvtvalue_id = self.env['hr.value.uvt.rf'].search(
                [('status', '=', True)])
            if uvtvalue_id:
                if reg.contract_completion_id:
                    if reg.employee_id.retention_method_id.name == '1':
                        for uvtitem in uvtvalue_id.range_retention_ids:
                            if reg.income_represented_uvt <\
                                    uvtitem.value_uvt_max and\
                                    reg.income_represented_uvt >\
                                    uvtitem.uvt_discount:
                                reg.percentage_renting_calculate =\
                                    uvtitem.marginal_rate / 100
                                result = 0
                                result = ((reg.income_represented_uvt -
                                           uvtitem.uvt_discount) *
                                          uvtvalue_id.value) * \
                                    uvtitem.marginal_rate / 100 + \
                                    (uvtitem.uvt_additional *
                                        uvtvalue_id.value)
                        if result_days < 0:
                            value_real_ret = (
                                round(result, -3) / basic_days) * (
                                result_days + 30)
                            value_month_before =\
                                reg.employee_id.get_value_line_payslip_before(
                                    reg, 'RETENCION EN LA FUENTE SALARIOS')
                            reg.total_retention_income = round(
                                (value_real_ret + value_month_before), -3)
                        elif days0:
                            date_before = reg.contract_completion_id.date
                            payslip_ids = self.env['hr.payslip'].search(
                                [('state', 'in', ['done', 'paid']),
                                 ('employee_id', '=', reg.employee_id.id),
                                 ('date_from', '<=', date_before),
                                 ('date_to', '>=', date_before),
                                 ])
                            result_days = sum(
                                [work_days.number_of_days for
                                 work_days
                                 in payslip_ids.worked_days_line_ids if
                                 work_days.name not in list_leave])
                            value_real_ret = (
                                round(result, -3) / basic_days) * (result_days)
                            value_month_before =\
                                reg.employee_id.get_value_line_payslip_before(
                                    reg, 'RETENCION EN LA FUENTE SALARIOS')
                            reg.total_retention_income = round(
                                (value_real_ret + value_month_before), -3)
                        else:
                            reg.total_retention_income = round(
                                ((result / basic_days) * result_days), -3)
                    elif reg.employee_id.retention_method_id.name == '2':
                        result = reg.base_income_retention *\
                            reg.employee_id.withholding_2
                        reg.percentage_renting_calculate =\
                            reg.employee_id.withholding_2
                        if result_days < 0:
                            value_month_before =\
                                reg.employee_id.get_value_line_payslip_before(
                                    reg, 'RETENCION EN LA FUENTE SALARIOS')
                            reg.total_retention_income = round(
                                (result + value_month_before), -3)
                        else:
                            reg.total_retention_income = round(result, -3)
                    else:
                        reg.total_retention_income = 0
                else:
                    if reg.employee_id.retention_method_id.name == '1':
                        for uvtitem in uvtvalue_id.range_retention_ids:
                            if reg.income_represented_uvt <\
                                    uvtitem.value_uvt_max and\
                                    reg.income_represented_uvt >\
                                    uvtitem.uvt_discount:
                                reg.percentage_renting_calculate =\
                                    uvtitem.marginal_rate / 100
                                result = 0
                                result = ((reg.income_represented_uvt -
                                           uvtitem.uvt_discount) *
                                          uvtvalue_id.value) * \
                                    uvtitem.marginal_rate / 100 + \
                                    (uvtitem.uvt_additional *
                                        uvtvalue_id.value)
                        reg.total_retention_income = round(
                            ((result / basic_days) * result_days), -3)
                    elif reg.employee_id.retention_method_id.name == '2':
                        result = reg.base_income_retention *\
                            reg.employee_id.withholding_2
                        reg.percentage_renting_calculate =\
                            reg.employee_id.withholding_2
                        reg.total_retention_income = round(
                            ((result / basic_days) * result_days), -3)
                    else:
                        reg.total_retention_income = 0
            else:
                reg.income_represented_uvt = (
                    result / basic_days) * result_days
        return result

    @api.depends('income_represented_uvt_cont', 'base_income_retention_cont')
    def _compute_total_retention_income_cont(self):
        result = 0
        for reg in self:
            leave_type_ids = self.env['hr.leave.type'].search(
                [('no_count_rent', '=', True)])
            list_leave = ()
            list_leaves = ''
            for lt_id in leave_type_ids:
                list_leaves += lt_id.name
            list_leave = (list_leaves)
            result_days = sum([work_days.number_of_days for work_days
                               in reg.worked_days_line_ids if
                               work_days.name not in list_leave])
            basic_days = 30
            if result_days > 30:
                basic_days = result_days
            if result_days == 0:
                result_days = 30
            uvtvalue_id = self.env['hr.value.uvt.rf'].search(
                [('status', '=', True)])
            if uvtvalue_id:
                if reg.employee_id.retention_method_id.name == '1':
                    for uvtitem in uvtvalue_id.range_retention_ids:
                        if reg.income_represented_uvt_cont <\
                            uvtitem.value_uvt_max\
                                and reg.income_represented_uvt_cont >\
                                uvtitem.uvt_discount:
                            reg.percentage_renting_calculate_cont =\
                                uvtitem.marginal_rate / 100
                            result = 0
                            # result = (reg.base_income_retention -
                            # (uvtvalue_id.value*
                            # uvtitem.uvt_discount)) *
                            # uvtitem.marginal_rate/100 +
                            # (uvtitem.uvt_additional * uvtvalue_id.value)
                            result = ((reg.income_represented_uvt_cont -
                                       uvtitem.uvt_discount) *
                                      uvtvalue_id.value)\
                                * uvtitem.marginal_rate / 100 +\
                                (uvtitem.uvt_additional * uvtvalue_id.value)
                    reg.total_retention_income_cont = (
                        round(result, -3) / basic_days) * result_days
                elif reg.employee_id.retention_method_id.name == '2':
                    result = reg.base_income_retention_cont *\
                        reg.employee_id.withholding_2
                    reg.percentage_renting_calculate_cont =\
                        reg.employee_id.withholding_2
                    reg.total_retention_income_cont = (
                        round(result, -3) / basic_days) * result_days
                else:
                    reg.total_retention_income_cont = 0
            else:
                reg.income_represented_uvt_cont = (
                    result / basic_days) * result_days
        return result

    @api.multi
    def compute_sheet_rf(self):
        """Define values sheet retention in page of payslip"""
        # Remove O2M Retention Pay

        for s_id in self:
            s_id.ps_input_rf_ids.unlink()
            s_id.ps_input_no_rf_ids.unlink()
            s_id.ps_deductions_ids.unlink()
            s_id.ps_renting_additional_ids.unlink()
            s_id.ps_exempt_income_ids.unlink()

            uvt_active = s_id.env['hr.value.uvt.rf'].search(
                [('status', '=', True)])
            if uvt_active:
                val_uvt = uvt_active.value
            else:
                return True

            leave_type_ids = self.env['hr.leave.type'].search(
                [('no_count_rent', '=', True)])
            list_leave = []
            list_leaves = ''
            for lt_id in leave_type_ids:
                list_leaves += lt_id.name
            list_leave = (list_leaves)
            result_days = sum([work_days.number_of_days for work_days
                               in s_id.worked_days_line_ids if
                               work_days.name not in list_leave])
            resultdays = result_days
            basic_days = 30
            if result_days > 30:
                basic_days = result_days
            if result_days == 0:
                result_days = 1
            mrt = 0
            mrt = self.employee_id.retention_method_id and\
                self.employee_id.retention_method_id.name
            if s_id.contract_completion_id and mrt == '1' and resultdays == 0:
                date_before = s_id.contract_completion_id.date
                payslip_ids = self.env['hr.payslip'].search(
                    [('state', 'in', ['done', 'paid']),
                     ('employee_id', '=', s_id.employee_id.id),
                     ('date_from', '<', date_before),
                     ('date_to', '>=', date_before),
                     ])
                for ps_line_id in payslip_ids.ps_input_rf_ids:
                    vals = {'name': ps_line_id.name,
                            'rule_id': ps_line_id.rule_id.id,
                            'sequence': ps_line_id.sequence,
                            'value_final': ps_line_id.value_final,
                            'hr_payslip_id': s_id.id,
                            }
                    s_id.env['hr.payslip.input.rf'].create(vals)
                for ps_line_id2 in payslip_ids.ps_input_no_rf_ids:
                    vals = {'name': ps_line_id2.name,
                            'rule_id': ps_line_id2.rule_id.id,
                            'sequence': ps_line_id2.sequence,
                            'value_final': ps_line_id2.value_final,
                            'hr_payslip_id': s_id.id,
                            }
                    s_id.env['hr.payslip.input.not.rf'].create(vals)
                result_days = sum([work_days.number_of_days for work_days
                                   in payslip_ids.worked_days_line_ids if
                                   work_days.name not in list_leave])
                for input_id in uvt_active.irf_rule_ids:
                    for ps_line_id in s_id.line_ids.filtered(
                            lambda x:
                            input_id.rule_id == x.salary_rule_id and
                            input_id.exempt_rm_id.name != mrt):
                        vals = {'name': input_id.name,
                                'rule_id': input_id.rule_id.id,
                                'sequence': input_id.sequence,
                                'value_final':
                                ps_line_id.salary_rule_id.projection_exempt and
                                ps_line_id.total or
                                (ps_line_id.total / result_days) * basic_days,
                                'hr_payslip_id': s_id.id,
                                }
                        s_id.env['hr.payslip.input.rf'].create(vals)
            else:
                for input_id in uvt_active.irf_rule_ids:
                    for ps_line_id in s_id.line_ids.filtered(
                            lambda x:
                            input_id.rule_id == x.salary_rule_id and
                            input_id.exempt_rm_id.name != mrt):
                        auxsign = 1
                        if ps_line_id.total > 0 and result_days < 0 and\
                                not\
                                ps_line_id.salary_rule_id.projection_exempt:
                            auxsign = -1
                        vals = {
                            'name': input_id.name,
                            'rule_id': input_id.rule_id.id,
                            'sequence': input_id.sequence,
                            'value_final': (
                                ps_line_id.salary_rule_id.projection_exempt and
                                ps_line_id.total or
                                (ps_line_id.total / result_days) *
                                basic_days) * auxsign,
                            'hr_payslip_id': s_id.id,
                        }
                        s_id.env['hr.payslip.input.rf'].create(vals)

            if s_id.contract_completion_id and mrt == '2' and resultdays < 0:
                for input_id in uvt_active.rule_ids:
                    for ps_line_id in s_id.line_ids.filtered(
                        lambda x: input_id.rule_id == x.salary_rule_id):
                        vals = {
                            'name': input_id.name,
                            'rule_id': input_id.rule_id.id,
                            'sequence': input_id.sequence,
                            'value_final':
                            ps_line_id.salary_rule_id.projection_exempt and
                            ps_line_id.total or
                            (ps_line_id.total / result_days) * (-(result_days +basic_days)),
                            'hr_payslip_id': s_id.id,
                        }
                        s_id.env['hr.payslip.input.not.rf'].create(vals)
            else:
                for input_id in uvt_active.rule_ids:
                    for ps_line_id in s_id.line_ids.filtered(
                            lambda x: input_id.rule_id == x.salary_rule_id):
                        vals = {
                            'name': input_id.name,
                            'rule_id': input_id.rule_id.id,
                            'sequence': input_id.sequence,
                            'value_final':
                            ps_line_id.salary_rule_id.projection_exempt and
                            ps_line_id.total or
                            (ps_line_id.total / result_days) * basic_days,
                            'hr_payslip_id': s_id.id,
                        }
                        s_id.env['hr.payslip.input.not.rf'].create(vals)

            for ded in s_id.employee_id.deductions_ids:
                sequence = ded.hr_deduction_type_id.sequence
                value_reference, value_final = ded.value, ded.value
                # Verificate dates available
                add_in_rent = False
                if not ded.start_date and not ded.end_date:
                    add_in_rent = True
                if ded.start_date and s_id.date_from <= ded.start_date and\
                        ded.end_date and s_id.date_to >= ded.end_date:
                    add_in_rent = True
                if not ded.start_date and\
                        ded.end_date and s_id.date_to >= ded.end_date:
                    add_in_rent = True
                if ded.start_date and\
                    s_id.date_from.month == ded.start_date.month and\
                        s_id.date_from.year == ded.start_date.year:
                    add_in_rent = True
                if ded.start_date and\
                    s_id.date_from.month >= ded.start_date.month and\
                        not ded.end_date:
                    add_in_rent = True
                if ded.start_date and s_id.date_from >= ded.start_date and\
                        ded.end_date and s_id.date_to <= ded.end_date:
                    add_in_rent = True
                if add_in_rent:
                    # Verificate limit value asigned for deductions
                    if ded.obtain_plines and ded.rule_id:
                        for line_id in s_id.line_ids:
                            if line_id.salary_rule_id.id == ded.rule_id.id:
                                value = 0
                                value = line_id.total
                                if value < 0:
                                    value = line_id.total * -1
                                value_reference, value_final = value, value

                    if ded.hr_deduction_id.dependent:
                        value_reference = s_id.inputs_rent
                        value_final = s_id.inputs_rent *\
                            ded.hr_deduction_id.max_percentage / 100
                    if ded.hr_deduction_id.max_uvt > 0:
                        val_max = val_uvt * ded.hr_deduction_id.max_uvt
                        if value_final > val_max:
                            value_final = val_max

                    if ded.hr_deduction_id.max_value > 0:
                        if value_final > ded.hr_deduction_id.max_value:
                            value_final = ded.hr_deduction_id.max_value
                    vals = {'hr_deductions_rf_employee_id': ded.id,
                            'sequence': sequence,
                            'value_reference': value_reference,
                            'value_final': value_final,
                            'hr_payslip_id': s_id.id,
                            }
                    s_id.env['hr.payslip.deductions.rf'].create(vals)
        return True

    @api.multi
    def compute_sheet(self):
        # self.onchange_employee()
        #super(HrPayslip, self).compute_sheet()
        # self.compute_sheet_rf()
        print("MAPFFF", self.name)
        return super(HrPayslip, self).compute_sheet()

    @api.model
    def create(self, vals):
        if not vals.get('percentage_renting_calculate'):
            vals['percentage_renting_calculate'] = 0
        employee_id = self.env['hr.employee'].browse(vals.get('employee_id'))
        if employee_id.retention_method_id.name == '2':
            vals['percentage_renting_calculate'] = employee_id.withholding_2
        return super(HrPayslip, self).create(vals)

    @api.multi
    def write(self, vals):
        if not vals.get('percentage_renting_calculate'):
            vals['percentage_renting_calculate'] = 0
        if vals.get('employee_id', False):
            employee_id = self.env['hr.employee'].browse(
                vals.get('employee_id'))
            if employee_id.retention_method_id.name == '2':
                vals['percentage_renting_calculate'] =\
                    employee_id.withholding_2
        return super(HrPayslip, self).write(vals)
