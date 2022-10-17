# Copyright 2020-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import datetime
import base64

from odoo import fields, models


def get_months():
    months_choices = []
    for month in range(1, 13):
        months_choices.append(
            (str(month).rjust(2, '0'), datetime.date(
                2019, month, 1).strftime('%B')))
    return months_choices


def get_years():
    years_choices = []
    for year in range(2000, 2101):
        years_choices.append(
            (str(year), str(year)))
    return years_choices


def get_date_combination(month, year):
    date_combination = []
    if month in ['01', '03', '05', '07', '08', '10', '12']:
        for date in range(1, 32):
            date_combination.append(year + '-' + month +
                                    '-' + str(date).rjust(2, '0'))
    if month in ['04', '06', '09', '11']:
        for date in range(1, 31):
            date_combination.append(year + '-' + month +
                                    '-' + str(date).rjust(2, '0'))
    if month in ['02']:
        if int(year) % 4 == 0:
            for date in range(1, 30):
                date_combination.append(year + '-' + month +
                                        '-' + str(date).rjust(2, '0'))
        if int(year) % 4 != 0:
            for date in range(1, 29):
                date_combination.append(year + '-' + month +
                                        '-' + str(date).rjust(2, '0'))
    return date_combination


class HrPayrollBancos(models.Model):
    """Hr Payroll Bancos."""
    _name = "hr.payroll.bancos"
    _rec_name = 'month'

    month = fields.Selection(get_months(), string="Month", required=True, copy=False)
    year = fields.Selection(get_years(), string="Year", required=True, copy=False)
    file = fields.Binary(copy=False)
    file_name = fields.Char(string='Name', size=64, copy=False)

    def action_generate_report(self):
        for rec in self:
            month = rec.month
            year = rec.year
            if len(month) == 1:
                month = "0" + month
            if month == '01':
                monthText = 'Ene'
            elif month == '02':
                monthText = 'Feb'
            elif month == '03':
                monthText = 'Mar'
            elif month == '04':
                monthText = 'Abr'
            elif month == '05':
                monthText = 'May'
            elif month == '06':
                monthText = 'Jun'
            elif month == '07':
                monthText = 'Jul'
            elif month == '08':
                monthText = 'Ago'
            elif month == '09':
                monthText = 'Sep'
            elif month == '10':
                monthText = 'Oct'
            elif month == '11':
                monthText = 'Nov'
            elif month == '12':
                monthText = 'Dic'
            header_content = '+----------------------------+------------------------------+-------------+---------------------+------------------+---------------------+-----------------------+-------------------------+--------------------------+----+---+---+-----------------------+--------------------+--------------------+--------------------+--------------------+--------------------+\n' + '|Tipo_identificacion_receptor|Numero_identificacion_receptor|Forma_de_pago|Codigo_banco_receptor|Numero_cuenta_BBVA|Tipo_de_cuenta_Nacham|Numero_de_cuenta_Nacham|Vr_operacion_parte_entera|Vr_operacion_parte_decimal| Ano|Mes|Dia|Codigo_Oficina_pagadora| Nombre_beneficiario|      Direccion_No_1|      Direccion_No_2|              E-mail|             concept|\n' + '+----------------------------+------------------------------+-------------+---------------------+------------------+---------------------+-----------------------+-------------------------+--------------------------+----+---+---+-----------------------+--------------------+--------------------+--------------------+--------------------+--------------------+'
            main_content = ''
            footer_content = '+----------------------------+------------------------------+-------------+---------------------+------------------+---------------------+-----------------------+-------------------------+--------------------------+----+---+---+-----------------------+--------------------+--------------------+--------------------+--------------------+--------------------+'
            for bank_rec in self.env['res.partner.bank'].search([]):

                Tipo_identificacion_receptor = ''
                if bank_rec.partner_id and bank_rec.partner_id.l10n_co_document_type:
                    Tipo_identificacion_receptor = bank_rec.partner_id.l10n_co_document_type

                Numero_identificacion_receptor = ''
                if bank_rec.partner_id and bank_rec.partner_id.vat:
                    Numero_identificacion_receptor = bank_rec.partner_id.vat

                Forma_de_pago = '1'

                Codigo_banco_receptor = ''
                if bank_rec.bank_id.bic:
                    Codigo_banco_receptor = bank_rec.bank_id.bic

                Numero_cuenta_BBVA = ''
                if bank_rec.acc_number:
                    Numero_cuenta_BBVA = bank_rec.acc_number

                Tipo_de_cuenta_Nacham = ''
                if bank_rec.type and bank_rec.type == 'current':
                    Tipo_de_cuenta_Nacham = '01'
                if bank_rec.type and bank_rec.type == 'savings':
                    Tipo_de_cuenta_Nacham = '02'

                Numero_de_cuenta_Nacham = ''
                if bank_rec.acc_number:
                    Numero_de_cuenta_Nacham = bank_rec.acc_number

                Vr_operacion_parte_entera = ''
                if bank_rec.partner_id:
                    employee = self.env['hr.employee'].search([
                        ('address_home_id', '=', bank_rec.partner_id.id)])
                    if employee:
                        total_amount = 0.0
                        for payslip in self.env['hr.payslip'].search([
                                ('employee_id', '=', employee.id),
                                ('date_from', 'in', get_date_combination(month, year)),
                                ('date_to', 'in', get_date_combination(month, year))]):
                            total_amount += payslip.total_amount
                        if total_amount > 0.0:
                            Vr_operacion_parte_entera = str(total_amount)

                Vr_operacion_parte_decimal = ''
                if bank_rec.partner_id:
                    employee = self.env['hr.employee'].search([
                        ('address_home_id', '=', bank_rec.partner_id.id)])
                    if employee:
                        total_amount = 0.0
                        for payslip in self.env['hr.payslip'].search([
                                ('employee_id', '=', employee.id),
                                ('date_from', 'in', get_date_combination(month, year)),
                                ('date_to', 'in', get_date_combination(month, year))]):
                            total_amount += payslip.total_amount
                        if total_amount > 0.0:
                            Vr_operacion_parte_decimal = str(round(total_amount))

                Ano = '0000'

                Mes = '00'

                Dia = '00'

                Codigo_Oficina_pagadora = '0000'

                Nombre_beneficiario = ''
                if bank_rec.partner_id and bank_rec.partner_id.name:
                    Nombre_beneficiario = bank_rec.partner_id.name

                Direccion_No_1 = 'BOGOTA'

                Direccion_No_2 = ''
                if bank_rec.partner_id and bank_rec.partner_id.street2:
                    Direccion_No_2 = bank_rec.partner_id.street2

                E_mail = ''
                if bank_rec.partner_id and bank_rec.partner_id.email:
                    Direccion_No_2 = bank_rec.partner_id.email

                concept = 'Voluntarios' + monthText
                main_content += '|' + Tipo_identificacion_receptor.rjust(28) + '|' +\
                    Numero_identificacion_receptor.rjust(30) + '|' +\
                    Forma_de_pago.rjust(13) + '|' +\
                    Codigo_banco_receptor.rjust(21) + '|' +\
                    Numero_cuenta_BBVA.rjust(18) + '|' +\
                    Tipo_de_cuenta_Nacham.rjust(21) + '|' +\
                    Numero_de_cuenta_Nacham.rjust(23) + '|' +\
                    Vr_operacion_parte_entera.rjust(25) + '|' +\
                    Vr_operacion_parte_decimal.rjust(26) + '|' +\
                    Ano.rjust(4) + '|' +\
                    Mes.rjust(3) + '|' +\
                    Dia.rjust(3) + '|' +\
                    Codigo_Oficina_pagadora.rjust(23) + '|' +\
                    Nombre_beneficiario.rjust(20) + '|' +\
                    Direccion_No_1.rjust(20) + '|' +\
                    Direccion_No_2.rjust(20) + '|' +\
                    E_mail.rjust(20) + '|' +\
                    concept.rjust(20) + '|' + '\n'
            data = header_content + main_content + footer_content
            filename = 'bancos_afc.txt'
            rec.write({'file': base64.b64encode(
                data.encode()), 'file_name': filename})
