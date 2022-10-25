# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta
import threading


class HrPayslipIwRecalc(models.Model):
    """Hr Payslip Iw Recalc."""

    _name = "hr.payslip.iw.recalc"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = "Hr Payslip Iw Recalc"

    name = fields.Char()
    date_start = fields.Date()
    date_end = fields.Date()
    state = fields.Selection(
        [("draft", "Draft"),
         ("open", "Open"),
         ("closed", "Closed")], default="draft"
    )
    calc_ids = fields.One2many(
        'hr.recalc.lines', 'hr_payslip_iw_recalc_id')
    reference = fields.Char(
        copy=False, readonly=True, default=lambda self: _('New'))

    @api.model
    def create(self, vals):
        """Create Sequence."""
        if vals.get('reference', _('New')) == _('New'):
            vals['reference'] = self.env['ir.sequence'].next_by_code(
                'hr.payslip.iw.recalc.sequence') or _('New')
        result = super(HrPayslipIwRecalc, self).create(vals)
        return result

    @api.multi
    def action_open(self):
        for rec in self:
            rec.state = 'open'

    @api.multi
    def action_move_draft(self):
        for rec in self:
            rec.state = 'draft'

    @api.multi
    def action_closed(self):
        for rec in self:
            ret_1 = self.env[
                'hr.retention.method.rf'].search([
                    ('name', '=', '1')], limit=1)
            ret_2 = self.env[
                'hr.retention.method.rf'].search([
                    ('name', '=', '2')], limit=1)
            for line in rec.calc_ids:
                if line.payslip_id and line.payslip_id.recalc:
                    line.payslip_id.action_payslip_cancel()
                if line.method_1:
                    if ret_1:
                        line.employee_id.write({
                            'retention_method_id': ret_1.id,
                            'withholding_2': 0.0})
                if line.method_2:
                    if ret_2:
                        line.employee_id.write({
                            'retention_method_id': ret_2.id,
                            'withholding_2':
                            line.total_retention_income / 100})
            rec.state = 'closed'

    @api.multi
    def action_compute_sheet_rf(self):
        for rec in self:
            for calc_id in rec.calc_ids:
                calc_id.compute_sheet_rf_thread()
            # rec.message_post(
            #     subject="Compute Sheet RF process generate correctly.",
            #     body=_("Compute Sheet RF process generate correctly"))


class HrRecalcLines(models.Model):
    """Hr Recalc Lines."""

    _name = "hr.recalc.lines"
    _description = "Hr Recalc Lines"
    _rec_name = 'hr_payslip_iw_recalc_id'

    hr_payslip_iw_recalc_id = fields.Many2one('hr.payslip.iw.recalc')
    employee_id = fields.Many2one(
        'hr.employee')
    percetage_result = fields.Float()
    ps_input_rf_ids = fields.One2many(
        'hr.rec.input.rf', 'rec_line_id',
        string='Input RF',
        help="The list of Inputs rf for employee")
    ps_input_no_rf_ids = fields.One2many(
        'hr.rec.input.not.rf', 'rec_line_id',
        string='Input no RF',
        help="The list of Inputs not rf for employee")
    sum_input_no_rf = fields.Float(compute='_calculate_sum_input_no_rf')
    ps_deductions_ids = fields.One2many(
        'hr.rec.deductions.rf', 'rec_line_id',
        string='Deductions',
        help="The list of deductions for employee",
        domain=[('sequence', '=', 2)])
    deductions = fields.Float(compute='_calculate_deductions')
    ps_renting_additional_ids = fields.One2many(
        'hr.rec.deductions.rf', 'rec_line_id',
        string='Renting Additional',
        help="The list of deductions for employee",
        domain=[('sequence', '=', 3)])
    rent_add = fields.Float(compute='_calculate_rent_add')
    total_base_retention = fields.Float(
        compute='_calculate_total_base_retention', store=True)
    ps_exempt_income_ids = fields.One2many(
        'hr.rec.deductions.rf', 'rec_line_id',
        string='Exempt Income',
        help="The list of exempt income",
        domain=[('sequence', '=', 4)])
    calculate_renting_exempt = fields.Float(
        string="calculate renting exempt renting",
        compute='_compute_calculate_renting_exempt',
        store=True)
    inputs_rent = fields.Float(
        string="Inputs Rent",
        compute='_compute_inputs_rent',
        store=True)
    subtotal_1 = fields.Float(
        string="Subtotal 1",
        compute='_compute_subtotal_1',
        store=True)
    subtotal_2 = fields.Float(
        string="Subtotal 2",
        compute='_compute_subtotal_2',
        store=True)
    total_renting_excempt = fields.Float(
        string="Total renting excempt",
        compute='_compute_total_renting_excempt',
        store=True)
    subtotal_3 = fields.Float(
        string="Subtotal 3",
        compute='_compute_subtotal_3',
        store=True)
    subtotal_4 = fields.Float(
        string="Subtotal 4",
        compute='_compute_subtotal_4',
        store=True)
    total_deductions_renting = fields.Float(
        string="Total Deductions and exempt renting",
        compute='_compute_total_deductions_renting',
        store=True)
    base_income_retention = fields.Float(
        string="Base Income Retention",
        compute='_compute_base_income_retention',
        store=True)
    income_represented_uvt = fields.Float(
        string="Income Represented UVT",
        compute='_compute_income_represented_uvt',
        store=True)
    method_2 = fields.Boolean(compute='_compute_method_one_two',
                              store=True)
    total_retention_income = fields.Float(
        string="Total Retention Income",
        compute='_compute_total_retention_income',
        store=True)
    method_1 = fields.Boolean(compute='_compute_method_one_two',
                              store=True)
    total_retention_method_1 = fields.Float(
        string="Total Retention Method 1",
        compute='_compute_total_retention_method_1',
        store=True)
    percentage_renting_calculate = fields.Float(
        string="Percentage Renting Calculate", digits=(32, 6))
    payslip_id = fields.Many2one('hr.payslip', "Payslip")
    state = fields.Selection(related='hr_payslip_iw_recalc_id.state',
                             store=True)
    name = fields.Char(compute='_compute_name')
    reference = fields.Char(
        copy=False, readonly=True, default=lambda self: _('New'))
    date_start = fields.Date()
    date_end = fields.Date()

    @api.model
    def create(self, vals):
        """Create Sequence."""
        if vals.get('reference', _('New')) == _('New'):
            vals['reference'] = self.env['ir.sequence'].next_by_code(
                'hr.recalc.lines.sequence') or _('New')
        result = super(HrRecalcLines, self).create(vals)
        if result.hr_payslip_iw_recalc_id and\
                result.hr_payslip_iw_recalc_id.date_start and\
                result.hr_payslip_iw_recalc_id.date_end:
            date_start = result.hr_payslip_iw_recalc_id.date_start
            date_end = result.hr_payslip_iw_recalc_id.date_end
            if self.employee_id.entry_date and\
                    result.hr_payslip_iw_recalc_id.date_start and\
                    self.employee_id.entry_date >=\
                    result.hr_payslip_iw_recalc_id.date_start:
                result.date_start = self.employee_id.entry_date
                month_add = result.hr_payslip_iw_recalc_id.date_end.month + 1
                result.date_end =\
                    result.hr_payslip_iw_recalc_id.date_end.replace(
                        month=month_add)
            else:
                result.date_start = date_start
                result.date_end = date_end
        return result

    @api.depends('ps_input_no_rf_ids', 'ps_input_no_rf_ids.value_final')
    def _calculate_sum_input_no_rf(self):
        for rec in self:
            result = 0.0
            if rec.state == 'draft':
                for line in rec.ps_input_no_rf_ids:
                    if line.value_final:
                        result += line.value_final
                rec.sum_input_no_rf = result

    @api.depends('ps_deductions_ids', 'ps_deductions_ids.value_final')
    def _calculate_deductions(self):
        for rec in self:
            result = 0.0
            if rec.state == 'draft':
                for line in rec.ps_deductions_ids:
                    if line.value_final:
                        result += line.value_final
                rec.deductions = result

    @api.depends('ps_renting_additional_ids',
                 'ps_renting_additional_ids.value_final')
    def _calculate_rent_add(self):
        for rec in self:
            result = 0.0
            if rec.state == 'draft':
                for line in rec.ps_renting_additional_ids:
                    if line.value_final:
                        result += line.value_final
                rec.rent_add = result

    @api.depends('subtotal_1', 'total_deductions_renting')
    def _calculate_total_base_retention(self):
        for rec in self:
            if rec.state == 'draft':
                if rec.subtotal_1 and rec.total_deductions_renting:
                    rec.total_base_retention = rec.subtotal_1 -\
                        rec.total_deductions_renting

    @api.depends('employee_id', 'hr_payslip_iw_recalc_id',
                 'hr_payslip_iw_recalc_id.name')
    def _compute_name(self):
        for rec in self:
            if rec.state == 'draft':
                if rec.employee_id and rec.hr_payslip_iw_recalc_id and\
                        rec.hr_payslip_iw_recalc_id.name:
                    rec.name = rec.employee_id.name + ' ' +\
                        rec.hr_payslip_iw_recalc_id.name

    @api.depends('ps_input_rf_ids')
    def _compute_inputs_rent(self):
        for reg in self:
            result = 0
            if reg.state == 'draft':
                for inputs in reg.ps_input_rf_ids:
                    result += inputs.value_final
                reg.inputs_rent = result

    @api.depends('ps_input_rf_ids', 'ps_input_no_rf_ids')
    def _compute_subtotal_1(self):
        for reg in self:
            if reg.state == 'draft':
                result = sum([inputs.value_final for inputs
                              in reg.ps_input_no_rf_ids])
                reg.subtotal_1 = reg.inputs_rent + result

    @api.depends('ps_deductions_ids', 'subtotal_1')
    def _compute_subtotal_2(self):
        for reg in self:
            result = 0
            if reg.state == 'draft':
                result = sum([deductions.value_final for deductions
                              in reg.ps_deductions_ids])
                reg.subtotal_2 = reg.subtotal_1 - result

    @api.depends('ps_renting_additional_ids', 'subtotal_1', 'subtotal_2',
                 'hr_payslip_iw_recalc_id.date_end',
                 'employee_id')
    def _compute_total_renting_excempt(self):
        for rec in self:
            result = 0
            if rec.state == 'draft':
                val_uvt = self.env['hr.value.uvt.rf'].search(
                    [('status', '=', True)])
                max_discount_value = val_uvt.r_ded_rent_exempt_value
                max_discount_percentage = (
                    val_uvt.r_ded_rent_exempt_percetage *
                    rec.subtotal_1) / 100
                result = sum([additionals.value_final for additionals
                              in rec.ps_renting_additional_ids])
                if result > max_discount_value:
                    result = max_discount_value
                if result > max_discount_percentage:
                    result = max_discount_percentage
                rec.total_renting_excempt = result

    @api.depends('total_renting_excempt', 'subtotal_1', 'subtotal_2')
    def _compute_subtotal_3(self):
        for reg in self:
            if reg.state == 'draft':
                reg.subtotal_3 = reg.subtotal_2 - reg.total_renting_excempt

    @api.depends('ps_exempt_income_ids', 'subtotal_1',
                 'subtotal_2', 'subtotal_3')
    def _compute_calculate_renting_exempt(self):
        result = 0
        active_uvt = self.env['hr.value.uvt.rf'].search([
            ('status', '=', True)])
        if not active_uvt:
            return result
        for reg in self:
            if reg.state == 'draft':
                result = \
                    reg.subtotal_3 * active_uvt.r_rent_exempt_percetage / 100
                if result > active_uvt.r_rent_exempt_value:
                    result = active_uvt.r_rent_exempt_value
                reg.calculate_renting_exempt = result

    @api.depends('ps_exempt_income_ids', 'subtotal_1',
                 'subtotal_2', 'subtotal_3', 'calculate_renting_exempt')
    def _compute_subtotal_4(self):
        for reg in self:
            if reg.state == 'draft':
                reg.subtotal_4 = reg.subtotal_3 - reg.calculate_renting_exempt

    @api.depends('subtotal_1', 'subtotal_2', 'subtotal_3', 'subtotal_4')
    def _compute_total_deductions_renting(self):
        result = 0
        percentage_salary = 0
        val_uvt = self.env['hr.value.uvt.rf'].search([('status', '=', True)])
        if not val_uvt:
            return result
        t_deduction = 0
        for reg in self:
            if reg.state == 'draft':
                t_deduction = sum([deductions.value_final for deductions
                                   in reg.ps_deductions_ids])
                t_deduction += reg.total_renting_excempt
                t_deduction += reg.calculate_renting_exempt
                result = t_deduction
                percentage_salary = reg.subtotal_1 * \
                    val_uvt.r_total_ded_exempt_percetage / 100
                if result > percentage_salary:
                    result = percentage_salary
                if val_uvt.r_total_ded_exempt_value > 0 and\
                        result > val_uvt.r_total_ded_exempt_value:
                    result = val_uvt.r_total_ded_exempt_value
                reg.total_deductions_renting = result

    @api.depends('total_deductions_renting')
    def _compute_base_income_retention(self):
        result = 0
        for reg in self:
            if reg.state == 'draft':
                result = reg.subtotal_1 - reg.total_deductions_renting
                start_date = reg.employee_id.entry_date
                end_date = reg.hr_payslip_iw_recalc_id.date_end
                date_diff = relativedelta(end_date, start_date)
                if result > 0:
                    if date_diff.years != None and date_diff.years >= 1:
                        if reg.payslip_id and\
                                reg.payslip_id.contract_completion_id:
                            reg.base_income_retention = result / 12
                        else:
                            reg.base_income_retention = result / 13
                    elif date_diff.months != None and date_diff.months > 0:
                        if reg.payslip_id and\
                                reg.payslip_id.contract_completion_id:
                            days = date_diff.days + date_diff.months * 30 + 1
                        else:
                            days = date_diff.days + date_diff.months * 30 + 30
                        reg.base_income_retention = result / (days) * 30
                    elif date_diff.days != None and date_diff.days > 0:
                        reg.base_income_retention = result / \
                            (date_diff.days + 31) * 30

    @api.depends('base_income_retention',
                 'employee_id')
    def _compute_income_represented_uvt(self):
        result = 0
        for reg in self:
            if reg.state == 'draft':
                val_uvt = self.env['hr.value.uvt.rf'].search(
                    [('status', '=', True)])
                if val_uvt:
                    if reg.base_income_retention != 0:
                        result = reg.base_income_retention / val_uvt.value
                        reg.income_represented_uvt = result
                else:
                    reg.income_represented_uvt = result

    @api.depends('total_retention_income', 'total_retention_method_1')
    def _compute_method_one_two(self):
        for rec in self:
            if rec.state == 'draft':
                if rec.employee_id.retention_method_id.name == '2':
                    rec.method_2 = True
                    rec.method_1 = False
                elif rec.total_retention_income < rec.total_retention_method_1:
                    rec.method_2 = True
                    rec.method_1 = False
                elif rec.total_retention_income > rec.total_retention_method_1:
                    rec.method_2 = False
                    rec.method_1 = True
                elif rec.total_retention_income ==\
                        rec.total_retention_method_1:
                    rec.method_2 = True
                    rec.method_1 = False

    @api.depends('income_represented_uvt', 'base_income_retention',
                 'employee_id', 'hr_payslip_iw_recalc_id.date_start',
                 'hr_payslip_iw_recalc_id.date_end')
    def _compute_total_retention_income(self):
        result = 0
        for reg in self:
            if reg.state == 'draft':
                if reg.date_start and\
                        reg.date_end and\
                        reg.employee_id:
                    if reg.payslip_id:
                        payslips = reg.payslip_id
                    else:
                        payslips = self.env['hr.payslip'].search(
                            [('date_from', '>=',
                              reg.date_start),
                             ('date_to', '<=',
                              reg.date_end),
                             ('employee_id', '=', reg.employee_id.id)])
                    for payslip in payslips:
                        if payslip.worked_days_line_ids:
                            uvtvalue_id = self.env['hr.value.uvt.rf'].search(
                                [('status', '=', True)])
                            if uvtvalue_id:
                                if reg.income_represented_uvt != 0:
                                    for uvtitem in\
                                            uvtvalue_id.range_retention_ids:
                                        if reg.income_represented_uvt <\
                                            uvtitem.value_uvt_max\
                                                and\
                                                reg.income_represented_uvt >\
                                                uvtitem.uvt_discount:
                                            reg.percentage_renting_calculate =\
                                                uvtitem.marginal_rate / 100
                                            result = 0
                                            result = (
                                                (reg.income_represented_uvt -
                                                 uvtitem.uvt_discount) *
                                                uvtvalue_id.value) * \
                                                uvtitem.marginal_rate / 100 + \
                                                (uvtitem.uvt_additional *
                                                 uvtvalue_id.value)
                                            result = result / \
                                                reg.base_income_retention * 100
                                    reg.total_retention_income = round(
                                        result, 2)
                            else:
                                reg.total_retention_income = 0

    @api.depends('payslip_id')
    def _compute_total_retention_method_1(self):
        for rec in self:
            if rec.state == 'draft':
                result = 0
                uvtvalue_id = self.env['hr.value.uvt.rf'].search(
                    [('status', '=', True)])
                if uvtvalue_id:
                    if rec.payslip_id.income_represented_uvt != 0:
                        for uvtitem in uvtvalue_id.range_retention_ids:
                            if rec.payslip_id.income_represented_uvt <\
                                uvtitem.value_uvt_max\
                                    and\
                                    rec.payslip_id.income_represented_uvt >\
                                    uvtitem.uvt_discount:
                                rec.payslip_id.percentage_renting_calculate =\
                                    uvtitem.marginal_rate / 100
                                result = 0
                                result = (
                                    (rec.payslip_id.income_represented_uvt -
                                     uvtitem.uvt_discount) *
                                    uvtvalue_id.value) * \
                                    uvtitem.marginal_rate / 100 + \
                                    (uvtitem.uvt_additional *
                                     uvtvalue_id.value)
                                result = result / \
                                    rec.payslip_id.base_income_retention * 100
                rec.total_retention_method_1 = result

    @api.multi
    def compute_sheet_rf(self):
        for rec_id in self:
            rec_id.ps_input_rf_ids.unlink()
            rec_id.ps_input_no_rf_ids.unlink()
            rec_id.ps_deductions_ids.unlink()
            rec_id.ps_renting_additional_ids.unlink()
            rec_id.ps_exempt_income_ids.unlink()
            uvt_active = rec_id.env['hr.value.uvt.rf'].search(
                [('status', '=', True)])
            if uvt_active:
                val_uvt = uvt_active.value
            else:
                return True
            if rec_id.date_start and\
                    rec_id.date_end and\
                    rec_id.employee_id:
                # if rec_id.payslip_id:
                #    payslips = rec_id.payslip_id
                date_start = rec_id.date_start
                date_end = rec_id.date_end
                if rec_id.employee_id.entry_date and\
                    rec_id.employee_id.entry_date > date_start and not\
                        rec_id.payslip_id.contract_completion_id:
                    if date_end.month >= 11:
                        month_project = 1
                        year_project = date_end.year + 1
                    else:
                        month_project = date_end.month + 2
                        year_project = date_end.year
                    date_end = date_end.replace(day=1, month=month_project,
                                                year=year_project)
                payslips = self.env['hr.payslip'].search(
                    [('date_from', '>=', date_start),
                     ('date_to', '<=', date_end),
                     ('employee_id', '=', rec_id.employee_id.id),
                     ('state', 'in', ('done', 'draft'))])
                for payslip in payslips:
                    if rec_id.payslip_id and rec_id.payslip_id.contract_completion_id:
                        days = sum([work_days.number_of_days for work_days
                                        in rec_id.payslip_id.worked_days_line_ids])                                    
                        for input_id in uvt_active.irf_rule_ids:
                            if payslip.date_to == date_end:
                                for ps_line_id in payslip.ps_input_rf_ids.filtered(
                                        lambda x:
                                        input_id.rule_id == x.rule_id):
                                    print("MAPFF", payslip.name, ps_line_id.name)
                                    vals = {'name': input_id.name,
                                            'rule_id': input_id.rule_id.id,
                                            'sequence': input_id.sequence,
                                            'value_final': ps_line_id.value_final/30 * days,
                                            'rec_line_id': rec_id.id,
                                            'payslip_id': payslip.id,
                                            }
                                    rec_id.env['hr.rec.input.rf'].create(vals)
                            elif payslip.date_from.month == date_end.month:
                                for ps_line_id in payslip.ps_input_rf_ids.filtered(
                                        lambda x:
                                        input_id.rule_id == x.rule_id):
                                    vals = {'name': input_id.name,
                                            'rule_id': input_id.rule_id.id,
                                            'sequence': input_id.sequence,
                                            'value_final': ps_line_id.value_final/30*(30-days),
                                            'rec_line_id': rec_id.id,
                                            'payslip_id': payslip.id,
                                            }
                                    rec_id.env['hr.rec.input.rf'].create(vals)
                            else:    
                                for ps_line_id in payslip.line_ids.filtered(
                                        lambda x:
                                        input_id.rule_id == x.salary_rule_id):
                                    vals = {'name': input_id.name,
                                            'rule_id': input_id.rule_id.id,
                                            'sequence': input_id.sequence,
                                            'value_final': ps_line_id.total,
                                            'rec_line_id': rec_id.id,
                                            'payslip_id': payslip.id,
                                            }
                                    rec_id.env['hr.rec.input.rf'].create(vals)
                    else:
                        for input_id in uvt_active.irf_rule_ids:
                            for ps_line_id in payslip.line_ids.filtered(
                                    lambda x:
                                    input_id.rule_id == x.salary_rule_id):
                                vals = {'name': input_id.name,
                                        'rule_id': input_id.rule_id.id,
                                        'sequence': input_id.sequence,
                                        'value_final': ps_line_id.total,
                                        'rec_line_id': rec_id.id,
                                        'payslip_id': payslip.id,
                                        }
                                rec_id.env['hr.rec.input.rf'].create(vals)
                        for input_id in uvt_active.rule_ids:
                            for ps_line_id in payslip.line_ids.filtered(
                                    lambda x:
                                    input_id.rule_id == x.salary_rule_id):
                                vals = {'name': input_id.name,
                                        'rule_id': input_id.rule_id.id,
                                        'sequence': input_id.sequence,
                                        'value_final': ps_line_id.total,
                                        'rec_line_id': rec_id.id,
                                        'payslip_id': payslip.id,
                                        }
                                rec_id.env['hr.rec.input.not.rf'].create(vals)
                        for ded in payslip.ps_deductions_ids:
                            vals = {'hr_deductions_rf_employee_id':
                                    ded.hr_deductions_rf_employee_id.id,
                                    'sequence': ded.sequence,
                                    'value_reference': ded.value_reference,
                                    'value_final': ded.value_final,
                                    'rec_line_id': rec_id.id,
                                    'payslip_id': payslip.id,
                                    }
                            rec_id.env['hr.rec.deductions.rf'].create(vals)
                        for ded in payslip.ps_renting_additional_ids:
                            vals = {'hr_deductions_rf_employee_id':
                                    ded.hr_deductions_rf_employee_id.id,
                                    'sequence': ded.sequence,
                                    'value_reference': ded.value_reference,
                                    'value_final': ded.value_final,
                                    'rec_line_id': rec_id.id,
                                    'payslip_id': payslip.id,
                                    }
                            rec_id.env['hr.rec.deductions.rf'].create(vals)
        return True

    def compute_sheet_rfs(self):
        with api.Environment.manage():
            new_cr = self.pool.cursor()
            new_self = self.with_env(self.env(cr=new_cr))
            new_self.compute_sheet_rf()
            new_cr.commit()
            new_cr.close()
            return {}

    def compute_sheet_rf_thread(self):
        threaded_calculation = threading.Thread(
            target=self.compute_sheet_rfs, args=())
        threaded_calculation.start()
        # self.hr_payslip_iw_recalc_id.message_post(
        #     subject="Compute Sheet RF process start.",
        #     body=_(
        #         "Compute Sheet RF Process:- %s Date:- %s Employee:- %s" % (
        #             threading.get_ident(), fields.Date.today(),
        #             self.employee_id.name)))
        return {'type': 'ir.actions.act_window_close'}


class HrRecInputRf(models.Model):
    """Hr Rec Input Rf."""

    _name = "hr.rec.input.rf"

    name = fields.Char(required=True)
    rule_id = fields.Many2one('hr.salary.rule', string="Rule", required="True")
    sequence = fields.Integer(string="Sequence")
    value_final = fields.Float(string="Value final", required=True)
    rec_line_id = fields.Many2one(
        'hr.recalc.lines', required=True, ondelete='cascade')
    payslip_id = fields.Many2one('hr.payslip', "Payslip")


class HrRecInputNotRf(models.Model):
    """Hr Rec Input Not Rf."""

    _name = "hr.rec.input.not.rf"

    name = fields.Char(required=True)
    rule_id = fields.Many2one('hr.salary.rule', string="Rule", required="True")
    sequence = fields.Integer(string="Sequence")
    value_final = fields.Float(string="Value final", required=True)
    rec_line_id = fields.Many2one(
        'hr.recalc.lines', required=True, ondelete='cascade')
    payslip_id = fields.Many2one('hr.payslip', "Payslip")


class HrRecDeductionsRf(models.Model):
    """Hr Rec Deductions Rf."""

    _name = "hr.rec.deductions.rf"

    hr_deductions_rf_employee_id = fields.Many2one(
        'hr.deductions.rf.employee', string="Deductions", required="True")
    hr_deduction_type_id = fields.Many2one(
        related="hr_deductions_rf_employee_id.hr_deduction_type_id")
    sequence = fields.Integer(string="Sequence")
    value_reference = fields.Float(string="Value Reference", required=True)
    value_final = fields.Float(string="Value final", required=True)
    rec_line_id = fields.Many2one(
        'hr.recalc.lines', required=True, ondelete='cascade')
    payslip_id = fields.Many2one('hr.payslip', "Payslip")
