# -*- coding: utf-8 -*-

from re import I
from odoo import api, models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pago_cesantias = fields.Date(string='Fecha Pago Cesantia', default='2021-02-05')
    pago_interes_cesantias = fields.Date(string='Fecha Pago I/Cesantias', default='2021-02-05')
    pago_prima1 = fields.Date(string='Fecha Pago Prima 1', default='2021-06-05')
    pago_prima2 = fields.Date(string='Fecha Pago Prima 2', default='2021-12-05')
    # Alertas
    alerta_pago_cesantias = fields.Date(string='Alerta Pago Cesantia')
    alerta_pago_interes_cesantias = fields.Date(string='Alerta Pago I/Cesantias')
    alerta_pago_prima1 = fields.Date(string='Alerta Pago Prima 1')
    alerta_pago_prima2 = fields.Date(string='Alerta Pago Prima 2')
    salario_minimo = fields.Char(string='Salario Mínimo')
    manual_payroll = fields.Boolean(string='Nómina Manual')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        IrCPSudo = self.env['ir.config_parameter'].sudo()
        res.update(
            pago_cesantias=IrCPSudo.get_param('hr_payroll_colombia.pago_cesantias'),
            pago_interes_cesantias=IrCPSudo.get_param('hr_payroll_colombia.pago_interes_cesantias'),
            pago_prima1=IrCPSudo.get_param('hr_payroll_colombia.pago_prima1'),
            pago_prima2=IrCPSudo.get_param('hr_payroll_colombia.pago_prima2'),
            alerta_pago_cesantias=IrCPSudo.get_param('hr_payroll_colombia.alerta_pago_cesantias'),
            alerta_pago_interes_cesantias=IrCPSudo.get_param('hr_payroll_colombia.alerta_pago_interes_cesantias'),
            alerta_pago_prima1=IrCPSudo.get_param('hr_payroll_colombia.alerta_pago_prima1'),
            alerta_pago_prima2=IrCPSudo.get_param('hr_payroll_colombia.alerta_pago_prima2'),
            salario_minimo=IrCPSudo.get_param('hr_payroll_colombia.salario_minimo'),
            manual_payroll=IrCPSudo.get_param('hr_payroll_colombia.manual_payroll'),
        )
        return res
    
    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        IrCPSudo = self.env['ir.config_parameter'].sudo()
        IrCPSudo.set_param('hr_payroll_colombia.pago_cesantias', self.pago_cesantias)
        IrCPSudo.set_param('hr_payroll_colombia.pago_interes_cesantias', self.pago_interes_cesantias)
        IrCPSudo.set_param('hr_payroll_colombia.pago_prima1', self.pago_prima1)
        IrCPSudo.set_param('hr_payroll_colombia.pago_prima2', self.pago_prima2)
        IrCPSudo.set_param('hr_payroll_colombia.alerta_pago_cesantias', self.alerta_pago_cesantias)
        IrCPSudo.set_param('hr_payroll_colombia.alerta_pago_interes_cesantias', self.alerta_pago_interes_cesantias)
        IrCPSudo.set_param('hr_payroll_colombia.alerta_pago_prima1', self.alerta_pago_prima1)
        IrCPSudo.set_param('hr_payroll_colombia.alerta_pago_prima2', self.alerta_pago_prima2)
        IrCPSudo.set_param('hr_payroll_colombia.salario_minimo', self.salario_minimo)
        IrCPSudo.set_param('hr_payroll_colombia.manual_payroll', self.manual_payroll)
