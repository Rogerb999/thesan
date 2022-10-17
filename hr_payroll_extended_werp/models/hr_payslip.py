# -*- coding: utf-8 -*-

import base64
import threading
from odoo import fields, models, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class HrPayslip(models.Model):
    _name = "hr.payslip"
    _inherit = ['hr.payslip', 'mail.thread', 'mail.activity.mixin']

    @api.depends('employee_id.address_home_id.vat')
    def _compute_identification_id(self):
        for rec in self:
            rec.identification_id = rec.employee_id.address_home_id.vat

    state = fields.Selection(
        selection_add=[('to_confirm', 'To Confirm'), ('paid', 'Paid')])
    total_amount = fields.Float(compute="_compute_total_amount", store=True)
    identification_id = fields.Char(
        compute='_compute_identification_id', string='Identification No',
        store=True)
    attachment_url = fields.Char("URL")
    journal_id = fields.Many2one(
        'account.journal', 'Salary Journal', readonly=True, required=True,
        states={'draft': [('readonly', False)]},
        default=lambda self: self.env['account.journal'].search([
            ('name', 'like', '%NOMINA%')], limit=1))
    pay_annual = fields.Boolean(
        'Pay Annual',
        readonly=True,
        states={'draft': [('readonly', False)]})
    pay_biannual = fields.Boolean(
        'Pay Biannual',
        readonly=True,
        states={'draft': [('readonly', False)]})
    pay_contributions = fields.Boolean(
        'Pay contributions',
        readonly=True,
        states={'draft': [('readonly', False)]})
    rule_ids = fields.Many2many('hr.salary.rule', string='Rules')
    total = fields.Float(compute="_compute_total", store=True)
    process_status = fields.Text()
    progress_action = fields.Char()
    description = fields.Text('Description Details')

    @api.multi
    @api.depends('line_ids')
    def _compute_total(self):
        for payslip in self:
            total = sum([line.total for line in payslip.line_ids.filtered(
                lambda x: x.salary_rule_id.total_cost)])
            payslip.total = total / 160 if total else 0.0

    @api.multi
    def action_to_confirm(self):
        self.state = 'to_confirm'

    @api.multi
    def action_pay(self):
        self.state = 'paid'

    @api.multi
    def action_payslip_cancel(self):
        return self.write({'state': 'cancel'})

    @api.multi
    def compute_sheet_all_thread(self):
        self.onchange_employee()
        super(HrPayslip, self).compute_sheet()
        self.compute_sheet_rf()
        res = super(HrPayslip, self).compute_sheet()
        self.message_post("The Calculate All Process Completed!")
        return res

    @api.multi
    def compute_sheet_all_thread_extended(self):
        try:
            with api.Environment.manage():
                new_cr = self.pool.cursor()
                self = self.with_env(self.env(cr=new_cr))
                self.compute_sheet_all_thread()
                new_cr.commit()
                new_cr.close()
            return {'type': 'ir.actions.act_window_close'}
        except Exception as error:
            _logger.info(error)

    @api.multi
    def compute_sheet_all(self):
        threaded_calculation = threading.Thread(target=self.with_context(
            progress_action=threading.get_ident(
            )).compute_sheet_all_thread_extended, args=())
        threaded_calculation.start()
        self.message_post(
            subject="Calculate All .",
            body=_(
                "The Calculate All is generating in this moment "
                "please wait Process:- %s Date:- %s" % (
                    threading.get_ident(), fields.Date.today())))

    @api.multi
    def action_payslip_done(self):
        res = super(HrPayslip, self).action_payslip_done()
        for slip in self:
            sum_days = 0.0
            if not self.env['hr.leave.allocation'].search([
                    ('payslip_id', '=', slip.id)]):
                for work_day in self.env['hr.payslip.worked_days'].search([
                        ('payslip_id', '=', slip.id)]):
                    sum_days += work_day.number_of_days
                if sum_days > 30.0:
                    sum_days = 30.0
                if slip.contract_id.leave_generate_id and sum_days > 0.0:
                    leave_generate_rec = slip.contract_id.leave_generate_id
                    self.env['hr.leave.allocation'].create({
                        'name': slip.number,
                        'holiday_type': 'employee',
                        'holiday_status_id': leave_generate_rec.leave_id.id,
                        'employee_id': slip.employee_id.id,
                        'number_of_days': 1.25 / 30 * sum_days,
                        'notes': 'HR Leave Generate via Payslip',
                        'payslip_id': slip.id})
                holiday_leave_type = self.env['hr.leave.type'].search([
                    ('name', '=', 'Vacaciones'),
                    ('request_unit', '=', 'day')])
                if holiday_leave_type and sum_days > 0.0:
                    holiday_leave = self.env['hr.leave.allocation'].create({
                        'name': slip.number,
                        'holiday_type': 'employee',
                        'holiday_status_id': holiday_leave_type.id,
                        'employee_id': slip.employee_id.id,
                        'number_of_days': 1.25 / 30 * sum_days,
                        'notes': 'Holiday Leave Generate via Payslip',
                        'payslip_id': slip.id})
                    holiday_leave.action_approve()
            att_id = slip.create_attachment_payslip()
            if att_id.url:
                slip.attachment_url = att_id.url
        return res

    # @api.multi
    # def action_payslip_done(self):
    #     res = super(HrPayslip, self).action_payslip_done()
    #     thread = threading.Thread(target=self.with_context(
    #         progress_action=threading.get_ident()).
    # action_payslip_done, args=())
    #     thread.start()

    '''
    @api.multi
    def action_payslip_done(self):
        res = super(HrPayslip, self).action_payslip_done()
        for slip in self:
            if slip.contract_id.leave_generate_id:
                leave_generate_rec = slip.contract_id.leave_generate_id
                self.env['hr.leave.allocation'].create({
                    'name': slip.number,
                    'holiday_type': 'employee',
                    'holiday_status_id': leave_generate_rec.leave_id.id,
                    'employee_id': slip.employee_id.id,
                    'number_of_days': leave_generate_rec.days,
                    'notes': 'HR Leave Generate via Payslip'})
            holiday_leave_type = self.env['hr.leave.type'].search([
                ('name', '=', 'Vacaciones'),
                ('request_unit', '=', 'day')])
            if holiday_leave_type:
                holiday_leave = self.env['hr.leave.allocation'].create({
                    'name': slip.number,
                    'holiday_type': 'employee',
                    'holiday_status_id': holiday_leave_type.id,
                    'employee_id': slip.employee_id.id,
                    'number_of_days': 1.25,
                    'notes': 'Holiday Leave Generate via Payslip'})
                holiday_leave.action_approve()
            att_id = slip.create_attachment_payslip()
            if att_id.url:
                slip.attachment_url = att_id.url
        return res
    '''

    @api.multi
    @api.depends('line_ids')
    def _compute_total_amount(self):
        for payslip in self:
            for line in payslip.line_ids.filtered(lambda x: x.code == 'NET'):
                payslip.total_amount = round(line.total)

    @api.multi
    def create_attachment_payslips(self):
        for slip in self:
            if slip.state == 'done':
                att_id = slip.create_attachment_payslip()
                if att_id.url:
                    slip.attachment_url = att_id.url

    @api.multi
    def create_attachment_payslip(self):
        report_id = self.env.ref('hr_payroll.action_report_payslip')
        pdf = report_id.render_qweb_pdf(self.ids)
        b64_pdf = base64.b64encode(pdf[0])
        att_name = _("Payslip %s from %s to %s" % (
            self.employee_id.name, self.date_from, self.date_to))

        att_id = self.env['ir.attachment'].create({
            'name': att_name,
            'type': 'binary',
            'datas': b64_pdf,
            'datas_fname': att_name + '.pdf',
            'store_fname': att_name,
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/x-pdf'
        })
        return att_id

    @api.multi
    def send_payslip_email(self):
        mail_template_id = self.env.ref(
            'hr_payroll_extended_werp.email_template_payslip_email')
        att_id = self.env['ir.attachment'].search([
            ('res_model', '=', 'hr.payslip'),
            ('res_id', '=', self.id)], limit=1)
        if not att_id:
            att_id = self.create_attachment_payslip()
        values = {
            'attachment_ids': [att_id.id],
        }
        if att_id.url:
            self.attachment_url = att_id.url
        mail_template_id.send_mail(self.id, email_values=values)

        return True

    @api.multi
    # def action_acumulate_thread(self):
    def action_acumulate(self):
        for rec in self:
            hr_rules_acumulate_ids = self.env['hr.conf.acumulated'].search([
                ('active', '!=', False)])
            employee_acumulate_ids = self.env['hr.employee.acumulate'].search(
                [('pay_slip_id', '=', self.id)])
            if employee_acumulate_ids:
                employee_acumulate_ids.unlink()
            for hr_rules_acumulate_id in hr_rules_acumulate_ids:
                for done_payslip in self.env['hr.payslip'].search(
                        [('id', '=', self.id)]):
                    if self.env['hr.employee.acumulate'].search(
                            [('pay_slip_id', '=', done_payslip.id),
                             ('hr_rules_acumulate_id', '=',
                                hr_rules_acumulate_id.id)]):
                        self.env['hr.employee.acumulate'].search(
                            [('pay_slip_id', '=', done_payslip.id),
                             ('hr_rules_acumulate_id', '=',
                                hr_rules_acumulate_id.id)]).unlink()
                    emp_acumulate =\
                        self.env['hr.employee.acumulate'].create({
                            'name':
                            'Acumulate for ' +
                            done_payslip.employee_id.name,
                            'employee_id': done_payslip.employee_id.id,
                            'pay_slip_id': done_payslip.id,
                            'hr_rules_acumulate_id':
                            hr_rules_acumulate_id.id,
                        })
                    self.env['hr.deduction.accumulate.rf'].search(
                        [('year', '=', str(fields.Date.today().year)),
                         ('employee_id', '=', rec.employee_id.id)]).unlink()
                    rec.employee_id.calculate_accumulate()
                    emp_acumulate.onchange_pay_slip_id()

    # def action_acumulates(self):
    #     with api.Environment.manage():
    #         new_cr = self.pool.cursor()
    #         new_self = self.with_env(self.env(cr=new_cr))
    #         new_self.action_acumulate_thread()
    #         if new_self._context.get('progress_action', ''):
    #             new_self.progress_action = new_self._context.get(
    #                 'progress_action', '')
    #         new_cr.commit()
    #         new_cr.close()
    #         return {}

    # @api.multi
    # def action_acumulate(self):
    #     """Create the acumulate."""
    #     threaded_calculation = threading.Thread(target=self.with_context(
    #         progress_action=threading.get_ident()).
    # action_acumulates, args=())
    #     threaded_calculation.start()
    #     self.message_post(
    #         subject="Accumulate process.",
    #         body=_(
    #             "The process Accumulate is generating in this moment "
    #             "please wait Process:- %s Date:- %s" % (
    #                 threading.get_ident(), fields.Date.today())))
    #     return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def unlink(self):
        if not self.env.user.has_group(
                'hr_payroll_extended_werp.group_payslip_delete'):
            raise UserError(_('You can not delete Payslip!'))
        return super(HrPayslip, self).unlink()

    @api.multi
    def action_payslip_review_parameters_thread(self):
        for rec in self:
            rec.onchange_employee()
        self.message_post("The Calculate Parameters Process Completed!")
        return True

    @api.multi
    def action_payslip_review_parameters_thread_extended(self):
        try:
            with api.Environment.manage():
                new_cr = self.pool.cursor()
                self = self.with_env(self.env(cr=new_cr))
                self.action_payslip_review_parameters_thread()
                new_cr.commit()
                new_cr.close()
            return {'type': 'ir.actions.act_window_close'}
        except Exception as error:
            _logger.info(error)

    @api.multi
    def action_payslip_review_parameters(self):
        threaded_calculation = threading.Thread(
            target=self.with_context(
                progress_action=threading.get_ident(
                )).action_payslip_review_parameters_thread_extended, args=())
        threaded_calculation.start()
        self.message_post(
            subject="Calculate All",
            body=_(
                "The Calculate Parameters is generating in this moment "
                "please wait Process:- %s Date:- %s" % (
                    threading.get_ident(), fields.Date.today())))

    @api.multi
    def action_payslip_caluculate_sheet(self):
        # def action_payslip_caluculate_sheet_thread(self):
        for rec in self:
            rec.compute_sheet()
            _logger.info(
                "===action_payslip_caluculate_sheet==%s==%s===>",
                rec, rec.name)
        # self.process_status = str(self.process_status + "Nómina Calculada")
        self.message_post("The Calculate payroll Process Completed!")
        return True

    # @api.multi
    # def action_payslip_caluculate_sheet_thread_extended(self):
    #     try:
    #         with api.Environment.manage():
    #             new_cr = self.pool.cursor()
    #             self = self.with_env(self.env(cr=new_cr))
    #             self.action_payslip_caluculate_sheet_thread()
    #             new_cr.commit()
    #             new_cr.close()
    #         return {'type': 'ir.actions.act_window_close'}
    #     except Exception as error:
    #         _logger.info(error)

    # @api.multi
    # def action_payslip_caluculate_sheet(self):
    #     threaded_calculation = threading.Thread(target=self.with_context(
    #         progress_action=threading.get_ident()).action_payslip_caluculate
    # sheet_thread_extended, args=())
    #     threaded_calculation.start()
    #     self.message_post(
    #         subject="Calculate payroll.",
    #         body=_(
    #             "The Calculate payroll is generating in this moment "
    #             "please wait Process:- %s Date:- %s" % (
    #                 threading.get_ident(), fields.Date.today())))

    @api.multi
    def action_payslip_calculate_retention(self):
        # def action_payslip_calculate_retention_thread(self):
        # super(HrPayslip, self).compute_sheet()
        for rec in self:
            rec.compute_sheet_rf()
            _logger.info(
                "===action_payslip_calculate_retention==%s==%s===>",
                rec, rec.name)
        # self.process_status = str(self.process_status +
        # "Retención Calculada")
        self.message_post("The Calculate RF Process Completed!")
        return True

    # @api.multi
    # def action_payslip_calculate_retention_thread_extended(self):
    #     try:
    #         with api.Environment.manage():
    #             new_cr = self.pool.cursor()
    #             self = self.with_env(self.env(cr=new_cr))
    #             self.action_payslip_calculate_retention_thread()
    #             new_cr.commit()
    #             new_cr.close()
    #         return {'type': 'ir.actions.act_window_close'}
    #     except Exception as error:
    #         _logger.info(error)

    # @api.multi
    # def action_payslip_calculate_retention(self):
    #     threaded_calculation = threading.Thread(target=self.with_context(
    #         progress_action=threading.get_ident()).action_payslip_calculate
    # retention_thread_extended, args=())
    #     threaded_calculation.start()
    #     self.message_post(
    #         subject="Calculate RF.",
    #         body=_(
    #             "The Calculate RF is generating in this moment "
    #             "please wait Process:- %s Date:- %s" % (
    #                 threading.get_ident(), fields.Date.today())))

    @api.multi
    def compute_sheet_thread(self):
        thread = threading.Thread(
            target=self.compute_sheet_sub_thread, args=())
        thread.start()

    @api.multi
    def compute_sheet_sub_thread(self):
        try:
            with api.Environment.manage():
                new_cr = self.pool.cursor()
                self = self.with_env(self.env(cr=new_cr))
                self.action_payslip_calculate_retention()
                self.action_payslip_caluculate_sheet()
                self.action_payslip_review_parameters()
                new_cr.commit()
                new_cr.close()
            return {'type': 'ir.actions.act_window_close'}
        except Exception as error:
            _logger.info(error)
            self.message_post(
                subject="Compute Sheet process.",
                body=_("The process Compute Sheet is not Completed"))

    @api.multi
    def compute_sheet(self):
        _logger.info("===compute_sheet==%s==%s===>", self, self.name)
        res = super(HrPayslip, self).compute_sheet()
        self.message_post(
            subject="Compute Sheet process.",
            body=_("The process Compute Sheet is Completed!"))
        return res

    # def compute_sheets(self):
    #     with api.Environment.manage():
    #         # As this function is in a new thread, I need to open a
    # new cursor, because the old one may be closed
    #         new_cr = self.pool.cursor()
    #         new_self = self.with_env(self.env(cr=new_cr))
    #         new_self.compute_sheet()
    #         if new_self._context.get('progress_action', ''):
    #             new_self.progress_action = new_self._context.get(
    #                 'progress_action', '')
    #         new_cr.commit()
        # new_cr.close()

    # @api.multi
    # def compute_sheet_thread(self):
    #     threaded_calculation = threading.Thread(
    #         target=self.with_context(
    #             progress_action=threading.get_ident()).
    # compute_sheets, args=())
    #     threaded_calculation.start()
    #     self.message_post(
    #         subject="Compute Sheet process.",
    #         body=_(
    #             "The process Compute Sheet is generating in this moment "
    #             "please wait Process:- %s Date:- %s" % (
    #                 threading.get_ident(), fields.Date.today())))
    #     return {'type': 'ir.actions.act_window_close'}


class HrPayslipRun(models.Model):
    _name = "hr.payslip.run"
    _inherit = ['hr.payslip.run', 'mail.thread', 'mail.activity.mixin']

    journal_id = fields.Many2one(
        'account.journal', 'Salary Journal',
        states={'draft': [('readonly', False)]}, readonly=True,
        required=True,
        default=lambda self: self.env['account.journal'].search([
            ('name', 'like', '%NOMINA%')], limit=1))
    pay_annual = fields.Boolean(
        'Pay Annual',
        states={'draft': [('readonly', False)]}, readonly=True)
    pay_biannual = fields.Boolean(
        'Pay Biannual',
        states={'draft': [('readonly', False)]}, readonly=True)
    rule_ids = fields.Many2many('hr.salary.rule', string='Rules')
    result_process = fields.Text("Result")
    state = fields.Selection(selection_add=[
        ('pending_confirm', 'Pending Confirm'),
        ('confirmed', 'Confirmed'),
        ('acumulate', 'Acumulate'),
        ('cancelled', 'Cancelled')])
    description = fields.Text('Description Details')
    pay_contributions = fields.Boolean(
        'Pay contributions',
        states={'draft': [('readonly', False)]}, readonly=True)

    @api.multi
    def send_payslip_run_email(self):
        for slip in self.slip_ids:
            slip.send_payslip_email()

    @api.multi
    def compute_sheet_thread(self):
        for rec in self:
            for line in rec.slip_ids:
                if line.state == 'draft':
                    line.compute_sheet_thread()

    @api.multi
    def compute_sheet(self):
        for rec in self:
            for line in rec.slip_ids:
                if line.state == 'draft':
                    line.compute_sheet()

    @api.multi
    def compute_sheet_all(self):
        for rec in self:
            for line in rec.slip_ids:
                if line.state == 'draft':
                    line.compute_sheet_all()

    @api.multi
    def action_to_confirm(self):
        for rec in self:
            for line in rec.slip_ids:
                if line.state == 'draft':
                    line.action_to_confirm()
            rec.write({'state': 'pending_confirm'})

    @api.multi
    def action_payslip_done_thread(self):
        thread = threading.Thread(target=self.with_context(
            progress_action=threading.get_ident(
            )).compute_action_payslip_done_thread, args=())
        thread.start()
        self.message_post(
            subject="Payslip Done Process...",
            body=_(
                "The Payslip Done process is generating in this moment "
                "please wait Process:- %s Date:- %s" % (
                    threading.get_ident(), fields.Date.today())))
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def compute_action_payslip_done_thread(self):
        try:
            with api.Environment.manage():
                new_cr = self.pool.cursor()
                self = self.with_env(self.env(cr=new_cr))
                self.action_payslip_done()
                new_cr.commit()
                new_cr.close()
            return {'type': 'ir.actions.act_window_close'}
        except Exception as error:
            _logger.info(error)

    @api.multi
    def action_payslip_done(self):
        for rec in self:
            for line in rec.slip_ids:
                if line.state == 'to_confirm':
                    _logger.info("action_payslip_done Line ====%s>>", line)
                    line.action_payslip_done()
                    line.action_acumulate()
            rec.write({'state': 'acumulate'})
            self.message_post("The Payslip process completed!")

    @api.multi
    def action_payslip_cancel(self):
        for rec in self:
            for line in rec.slip_ids:
                if line.state != 'done' or line.state != 'paid':
                    line.action_payslip_cancel()
            rec.write({'state': 'cancelled'})

    @api.multi
    def action_accumulate_thread(self):
        thread = threading.Thread(target=self.with_context(
            progress_action=threading.get_ident(
            )).compute_action_accumulate_thread, args=())
        thread.start()
        self.message_post(
            subject="Accumulate Process...",
            body=_(
                "The Accumulate process is generating in this moment "
                "please wait Process:- %s Date:- %s" % (
                    threading.get_ident(), fields.Date.today())))
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def compute_action_accumulate_thread(self):
        try:
            with api.Environment.manage():
                new_cr = self.pool.cursor()
                self = self.with_env(self.env(cr=new_cr))
                self.action_acumulate()
                new_cr.commit()
                new_cr.close()
            return {'type': 'ir.actions.act_window_close'}
        except Exception as error:
            _logger.info(error)

    @api.multi
    def action_acumulate(self):
        for rec in self:
            for line in rec.slip_ids:
                if line.state == 'done':
                    _logger.info("action_accumulate Line ====%s>>", line)
                    line.action_acumulate()
            rec.write({'state': 'acumulate'})
            self.message_post("Accumulate Process Completed!")

    @api.multi
    def action_payslip_draft(self):
        for rec in self:
            aux = 0
            for line in rec.slip_ids:
                if line.state == 'cancel':
                    line.action_payslip_draft()
            rec.write({'state': 'draft'})

    @api.multi
    def action_payslip_review_parameters(self):
        for rec in self:
            aux = 0
            for line in rec.slip_ids:
                if line.state == 'draft':
                    aux += 1
                    _logger.info(
                        "===action_payslip_review_parameters==%s==%s===>",
                        aux, line.employee_id.name)
                    line.action_payslip_review_parameters()

    @api.multi
    def action_payslip_calculate_retention_thread(self):
        for rec in self:
            aux = 0
            for line in rec.slip_ids:
                if line.state == 'draft':
                    aux += 1
                    _logger.info(
                        "===action_payslip_calculate_retention==%s==%s===>",
                        aux, line.employee_id.name)
                    line.action_payslip_calculate_retention()

    @api.multi
    def action_payslip_calculate_retention_thread_extended(self):
        try:
            with api.Environment.manage():
                new_cr = self.pool.cursor()
                self = self.with_env(self.env(cr=new_cr))
                self.action_payslip_calculate_retention_thread()
                new_cr.commit()
                new_cr.close()
            return {'type': 'ir.actions.act_window_close'}
        except Exception as error:
            _logger.info(error)

    @api.multi
    def action_payslip_calculate_retention(self):
        threaded_calculation = threading.Thread(target=self.with_context(
            progress_action=threading.get_ident(
            )).action_payslip_calculate_retention_thread_extended, args=())
        threaded_calculation.start()
        self.message_post(
            subject="Calculate RF/Withholding Income.",
            body=_(
                "The Calculate RF/Withholding Income "
                "is generating in this moment "
                "please wait Process:- %s Date:- %s" % (
                    threading.get_ident(), fields.Date.today())))

    @api.multi
    def action_payslip_caluculate_sheet_thread(self):
        for rec in self:
            aux = 0
            for line in rec.slip_ids:
                if line.state == 'draft':
                    aux += 1
                    _logger.info(
                        "=action_payslip_caluculate_sheet_thread==%s==%s=>",
                        aux, line.employee_id.name)
                    line.action_payslip_caluculate_sheet()
            rec.message_post("The Calculate payroll Process Completed!")

    @api.multi
    def action_payslip_caluculate_sheet_thread_extended(self):
        try:
            with api.Environment.manage():
                new_cr = self.pool.cursor()
                self = self.with_env(self.env(cr=new_cr))
                self.action_payslip_caluculate_sheet_thread()
                new_cr.commit()
                new_cr.close()
            return {'type': 'ir.actions.act_window_close'}
        except Exception as error:
            _logger.info(error)

    @api.multi
    def action_payslip_caluculate_sheet(self):
        threaded_calculation = threading.Thread(target=self.with_context(
            progress_action=threading.get_ident(
            )).action_payslip_caluculate_sheet_thread_extended, args=())
        threaded_calculation.start()
        self.message_post(
            subject="Calculate payroll.",
            body=_(
                "The Calculate payroll is generating in this moment "
                "please wait Process:- %s Date:- %s" % (
                    threading.get_ident(), fields.Date.today())))

    @api.multi
    def create_attachment_payslips(self):
        for rec in self:
            for line in rec.slip_ids:
                line.create_attachment_payslips()


class HrPayslipLine(models.Model):
    _inherit = "hr.payslip.line"

    @api.model
    def create(self, vals):
        if self._context.get('transfer_data', '') and not vals.get(
                'slip_id', '') or not vals.get(
                    'salary_rule_id', '') or not vals.get(
                        'employee_id', '') or not vals.get('contract_id', ''):
            return False
        return super(HrPayslipLine, self).create(vals)

    @api.multi
    @api.depends('salary_rule_id', 'salary_rule_id.work_days_value', 'slip_id')
    def _compute_days(self):
        for rec in self:
            if rec.salary_rule_id and rec.salary_rule_id.work_days_value:
                days = 0.0
                for worked_days in self.env[
                        'hr.payslip.worked_days'].search([
                            ('payslip_id', '=', rec.slip_id.id),
                            ('code', 'in',
                             [code.strip() for code in
                              rec.salary_rule_id.work_days_value.split(
                                  ',')])]):
                    days += worked_days.number_of_days
                rec.days = days

    @api.multi
    @api.depends('salary_rule_id', 'salary_rule_id.model',
                 'salary_rule_id.asigned_base',
                 'salary_rule_id.field',
                 'salary_rule_id.value',
                 'salary_rule_id.categ',
                 'slip_id', 'category_id', 'category_id.code', 'total')
    def _compute_base(self):
        for rec in self:
            base = 0.0
            if rec.salary_rule_id.asigned_base == 'value' and\
                    rec.salary_rule_id.value:
                base = rec.salary_rule_id.value
            if rec.salary_rule_id.asigned_base == 'model' and\
                    rec.salary_rule_id.model and rec.salary_rule_id.field:
                if rec.salary_rule_id.model.model == 'hr.contract':
                    data = rec.slip_id.contract_id.read(
                        [rec.salary_rule_id.field.name])
                    if data:
                        base = data[0].get(rec.salary_rule_id.field.name)
            if rec.salary_rule_id.asigned_base == 'categ' and\
                    rec.salary_rule_id.categ:
                for line in self.search([
                        ('slip_id', '=', rec.slip_id.id)]):
                    if line.category_id and line.category_id.code:
                        if line.category_id.code in [
                                x.strip() for x in
                                rec.salary_rule_id.categ.split(',')] and\
                                line.total:
                            base += line.total
            rec.base = base

    days = fields.Float(compute='_compute_days', store=True)
    base = fields.Float(compute='_compute_base', store=True)
    description = fields.Text('Description Details')
