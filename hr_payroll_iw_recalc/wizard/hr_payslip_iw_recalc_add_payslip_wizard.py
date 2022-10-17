# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


class HrPayslipIwRecalcAddPayslipWizard(models.TransientModel):
    """Hr Payslip Iw Recalc Add Payslip Wizard."""

    _name = "hr.payslip.iw.recalc.add.payslip.wizard"

    @api.model
    def default_get(self, default_fields):
        """Fill Data."""
        rec = super(HrPayslipIwRecalcAddPayslipWizard, self).default_get(
            default_fields)
        context = self._context
        if context.get('active_model', '') and context.get('active_id', ''):
            if context.get('active_model', '') == 'hr.payslip.iw.recalc':
                hr_payslip_iw_recalc_rec = self.env[context.get(
                    'active_model', '')].browse(context.get('active_id', ''))
                if hr_payslip_iw_recalc_rec.calc_ids:
                    rec.update({
                        'employee_ids': hr_payslip_iw_recalc_rec.mapped(
                            'calc_ids.employee_id').ids,
                        'date_start': hr_payslip_iw_recalc_rec.date_start,
                        'date_end': hr_payslip_iw_recalc_rec.date_end})
            if context.get('active_model', '') == 'hr.recalc.lines':
                hr_recalc_lines_rec = self.env[context.get(
                    'active_model', '')].browse(context.get('active_id', ''))
                if hr_recalc_lines_rec:
                    rec.update({
                        'employee_ids': hr_recalc_lines_rec.employee_id.ids,
                        'date_start':
                        hr_recalc_lines_rec.hr_payslip_iw_recalc_id.date_start,
                        'date_end':
                        hr_recalc_lines_rec.hr_payslip_iw_recalc_id.date_end})
        return rec

    employee_ids = fields.Many2many(
        'hr.employee')
    date_start = fields.Date()
    date_end = fields.Date()

    @api.multi
    def create_payslips(self):
        """Generate Payslip."""
        for rec in self:
            if rec.employee_ids and rec.date_start and rec.date_end:
                for employee in rec.employee_ids:
                    contract = self.env['hr.payslip'].get_contract(
                        employee, rec.date_start, rec.date_end)
                    if self._context.get(
                            'active_model', '') and self._context.get(
                            'active_id', '') and contract:
                        if self._context.get('active_model', '') ==\
                                'hr.payslip.iw.recalc':
                            hr_payslip_iw_recalc_rec = self.env[
                                self._context.get(
                                    'active_model', '')].browse(
                                self._context.get('active_id', ''))
                            if hr_payslip_iw_recalc_rec:
                                hr_recalc_lines_rec = self.env[
                                    'hr.recalc.lines'].search([
                                        ('employee_id', '=', employee.id),
                                        ('hr_payslip_iw_recalc_id', '=',
                                         hr_payslip_iw_recalc_rec.id)], limit=1
                                )
                                payslip = self.env['hr.payslip'].create({
                                    'employee_id': employee.id,
                                    'date_from': rec.date_start,
                                    'date_to': rec.date_end,
                                    'name': employee.name,
                                    'contract_id': contract[0],
                                    'recalc': True
                                })
                                payslip.onchange_employee()
                                if hr_recalc_lines_rec and payslip:
                                    hr_recalc_lines_rec.write({
                                        'payslip_id': payslip.id})
                                bck_method = employee.retention_method_id
                                hr_retention_method_rf_obj = self.env[
                                    'hr.retention.method.rf'].search([
                                        ('name', '=', '1')], limit=1)
                                if hr_retention_method_rf_obj:
                                    employee.write({
                                        'retention_method_id':
                                        hr_retention_method_rf_obj.id})
                                payslip.compute_sheet_all_thread()
                                if hr_recalc_lines_rec and payslip:
                                    hr_recalc_lines_rec.write({
                                        'payslip_id': payslip.id})
                                employee.write(
                                    {'retention_method_id': bck_method.id})
                                payslip.write({
                                    'name': 'Recalc ' + payslip.name})
                        if self._context.get('active_model', '') ==\
                                'hr.recalc.lines':
                            hr_recalc_lines_rec = self.env[
                                self._context.get(
                                    'active_model', '')].browse(
                                        self._context.get(
                                            'active_id', ''))
                            if hr_recalc_lines_rec:
                                payslip = self.env['hr.payslip'].create({
                                    'employee_id': employee.id,
                                    'date_from': rec.date_start,
                                    'date_to': rec.date_end,
                                    'name': employee.name,
                                    'contract_id': contract[0],
                                    'recalc': True
                                })
                                payslip.onchange_employee()
                                bck_method = employee.retention_method_id
                                hr_retention_method_rf_obj = self.env[
                                    'hr.retention.method.rf'].search([
                                        ('name', '=', '1')], limit=1)
                                if hr_retention_method_rf_obj:
                                    employee.write({
                                        'retention_method_id':
                                        hr_retention_method_rf_obj.id})
                                payslip.compute_sheet_all_thread()
                                if hr_recalc_lines_rec and payslip:
                                    hr_recalc_lines_rec.write({
                                        'payslip_id': payslip.id})
                                employee.write(
                                    {'retention_method_id': bck_method.id})
                                payslip.write({
                                    'name': 'Recalc ' + payslip.name})
