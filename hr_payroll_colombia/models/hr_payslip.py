# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from odoo import api, models, fields


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'
    
    contract_schedule_pay = fields.Selection(related='contract_id.contract_schedule_pay', string='Pago Por Contrato')
    febrary_month = fields.Boolean(string='Mes Febrero', compute='_validate_febrary_month', default=False)
    pay_days = fields.Boolean(string='Pago por Días', default=False)
    
    @api.depends('date_from')
    def _validate_febrary_month(self):
        for item in self:
            if item.date_from.month == 2:
                item.febrary_month = True

    @api.model
    def get_worked_day_lines(self, contracts, date_from, date_to):
        res = super(HrPayslip, self).get_worked_day_lines(contracts, date_from, date_to)
        for item in res:
            if 'WORK100' in item['code']:
                item['code'] = 'DiasTrabajados'
        return res
    
    @api.onchange('employee_id')
    def _get_bono_rodamiento(self):
        if self.employee_id:
            self.input_line_ids = [(5, 0, {})]
            adicionales = []

            # Bono
            adicionales = [(0, 0, {
                'name': 'Bono',
                'code': 'Bono',
                'amount': 0,
                #'contract_id': self.employee_id.contract_id.id
            })]

            # Rodamiento
            adicionales += [(0, 0, {
                'name': 'Rodamiento',
                'code': 'Rodamiento',
                'amount': 0,
                #'contract_id': self.employee_id.contract_id.id
            })]

            # Prestamo
            adicionales += [(0, 0, {
                'name': 'Prestamo',
                'code': 'DEUDA',
                'amount': 0,
                #'contract_id': self.employee_id.contract_id.id
            })]

            self.input_line_ids = adicionales
    
    def action_payslip_done(self):
        res = super(HrPayslip, self).action_payslip_done()
        cesantias_mes = self.line_ids.filtered(lambda x: x.code == 'Cesantias_mensual')
        if cesantias_mes:
            self.employee_id.write({
                'total_cesantias': cesantias_mes.total
            })
        return res
