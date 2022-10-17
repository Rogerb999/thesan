# Copyright 2020-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import datetime
import base64
import xlsxwriter

from odoo import fields, models, _


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


class PagoNominaReport(models.Model):
    """Pago Nomina Report."""
    _name = "pago.nomina.report"
    _rec_name = 'month'

    month = fields.Selection(
        get_months(), string="Month", required=True, copy=False)
    year = fields.Selection(get_years(), string="Year",
                            required=True, copy=False)
    file = fields.Binary(copy=False)
    file_name = fields.Char(string='Name', size=64, copy=False)
    file_sheet = fields.Binary(copy=False)
    file_sheet_name = fields.Char(string='Name', size=64, copy=False)

    def action_generate_report(self):
        for rec in self:
            month = rec.month
            year = rec.year
            header_content = '+-------------+-----------+----------+----------+-------------+--------------------+--------+--------------+-------+------+--------------------+------------+------------------+------------+---------+-----------+---------------+-------------+-------------+-----------+-----------+\n' + \
                '|nombreempresa|        nit|  contrato|identifica|tipoDocumento|              nombre|concepto|codigoConcepto|f_valor|f_base|      conceptonombre|tipoconcepto|nombrecargoencargo|fechaingreso|   sueldo|nombrecargo|codcargofuncion|nombreentidad|codigoentidad|codigo_sara|fbasedinero|\n' + \
                '+-------------+-----------+----------+----------+-------------+--------------------+--------+--------------+-------+------+--------------------+------------+------------------+------------+---------+-----------+---------------+-------------+-------------+-----------+-----------+\n'
            main_content = ''
            footer_content = '+-------------+-----------+----------+----------+-------------+--------------------+--------+--------------+-------+------+--------------------+------------+------------------+------------+---------+-----------+---------------+-------------+-------------+-----------+-----------+'
            file_path = 'pago_nomina' + '.xlsx'
            workbook = xlsxwriter.Workbook('/tmp/' + file_path)
            worksheet = workbook.add_worksheet("Pago Nomina")
            worksheet.write('A1', _('nombreempresa'))
            worksheet.write('B1', _('nit'))
            worksheet.write('C1', _('contrato'))
            worksheet.write('D1', _('identifica'))
            worksheet.write('E1', _('tipoDocumento'))
            worksheet.write('F1', _('nombre'))
            worksheet.write('G1', _('concepto'))
            worksheet.write('H1', _('codigoConcepto'))
            worksheet.write('I1', _('f_valor'))
            worksheet.write('J1', _('f_base'))
            worksheet.write('K1', _('conceptonombre'))
            worksheet.write('L1', _('tipoconcepto'))
            worksheet.write('M1', _('nombrecargoencargo'))
            worksheet.write('N1', _('fechaingreso'))
            worksheet.write('O1', _('sueldo'))
            worksheet.write('P1', _('nombrecargo'))
            worksheet.write('Q1', _('codcargofuncion'))
            worksheet.write('R1', _('nombreentidad'))
            worksheet.write('S1', _('codigoentidad'))
            worksheet.write('T1', _('codigo_sara'))
            worksheet.write('U1', _('fbasedinero'))
            column = 1
            for payslip_line in self.env['hr.payslip.line'].search([
                    ('slip_id.date_from', 'in', get_date_combination(month, year)),
                    ('slip_id.date_to', 'in', get_date_combination(month, year))]):
                column += 1
                nombreempresa = ''
                if payslip_line.slip_id.company_id:
                    nombreempresa = payslip_line.slip_id.company_id.display_name
                nit = ''
                if payslip_line.slip_id.employee_id.address_home_id and payslip_line.slip_id.employee_id.address_home_id.vat:
                    nit = payslip_line.slip_id.employee_id.address_home_id.vat
                contrato = ''
                if payslip_line.slip_id.identification_id:
                    contrato = payslip_line.slip_id.identification_id
                identifica = ''
                if payslip_line.slip_id.identification_id:
                    identifica = payslip_line.slip_id.identification_id
                tipoDocumento = ''
                if payslip_line.slip_id.employee_id.address_home_id and payslip_line.slip_id.employee_id.address_home_id.l10n_co_document_type:
                    tipoDocumento = payslip_line.slip_id.employee_id.address_home_id.l10n_co_document_type
                nombre = ''
                if payslip_line.slip_id.employee_id:
                    nombre = payslip_line.slip_id.employee_id.display_name
                concepto = ''
                if payslip_line.sequence:
                    if str(payslip_line.sequence) not in ['17', '43', '45', '46', '48', '121', '199', '200', '300', '350', '500', '501', '502', '503', '504', '505', '506', '507', '508', '509', '510', '511', '512', '513', '514', '515', '516', '518', '519', '520', '524', '525', '528', '600', '601', '602']:
                        concepto = str(payslip_line.sequence)
                codigoConcepto = ''
                f_valor = ''
                if payslip_line.total:
                    f_valor = str(payslip_line.total)
                f_base = ''
                conceptonombre = ''
                if payslip_line.name:
                    conceptonombre = payslip_line.name
                tipoconcepto = ''
                if payslip_line.account_debit:
                    tipoconcepto = '+'
                if payslip_line.account_credit:
                    tipoconcepto = '-'
                if not payslip_line.account_debit or payslip_line.account_credit:
                    tipoconcepto = ''
                nombrecargoencargo = ''
                fechaingreso = ''
                if payslip_line.slip_id.contract_id and payslip_line.slip_id.contract_id.date_start:
                    fechaingreso = str(
                        payslip_line.slip_id.contract_id.date_start)
                sueldo = ''
                if payslip_line.slip_id.contract_id and payslip_line.slip_id.contract_id.fix_wage_amount:
                    fechaingreso = str(
                        payslip_line.slip_id.contract_id.fix_wage_amount)
                nombrecargo = ''
                codcargofuncion = ''
                nombreentidad = ''
                codigoentidad = ''
                codigo_sara = ''
                if payslip_line.salary_rule_id and payslip_line.salary_rule_id.code_sara:
                    codigo_sara = payslip_line.salary_rule_id.code_sara
                fbasedinero = ''
                if payslip_line.base:
                    fbasedinero = str(payslip_line.salary_rule_id.calculate_base)
                main_content += '|' + nombreempresa.rjust(13) + '|' +\
                    nit.rjust(11) + '|' +\
                    contrato.rjust(10) + '|' +\
                    identifica.rjust(10) + '|' +\
                    tipoDocumento.rjust(13) + '|' +\
                    nombre.rjust(20) + '|' +\
                    concepto.rjust(8) + '|' +\
                    codigoConcepto.rjust(14) + '|' +\
                    f_valor.rjust(7) + '|' +\
                    f_base.rjust(6) + '|' +\
                    conceptonombre.rjust(20) + '|' +\
                    tipoconcepto.rjust(12) + '|' +\
                    nombrecargoencargo.rjust(18) + '|' +\
                    fechaingreso.rjust(12) + '|' +\
                    sueldo.rjust(9) + '|' +\
                    nombrecargo.rjust(11) + '|' +\
                    codcargofuncion.rjust(15) + '|' +\
                    nombreentidad.rjust(13) + '|' +\
                    codigoentidad.rjust(13) + '|' +\
                    codigo_sara.rjust(11) + '|' +\
                    fbasedinero.rjust(11) + '|' + '\n'
                worksheet.write('A' + str(column), nombreempresa)
                worksheet.write('B' + str(column), nit)
                worksheet.write('C' + str(column), contrato)
                worksheet.write('D' + str(column), identifica)
                worksheet.write('E' + str(column), tipoDocumento)
                worksheet.write('F' + str(column), nombre)
                worksheet.write('G' + str(column), concepto)
                worksheet.write('H' + str(column), codigoConcepto)
                worksheet.write('I' + str(column), f_valor)
                worksheet.write('J' + str(column), f_base)
                worksheet.write('K' + str(column), conceptonombre)
                worksheet.write('L' + str(column), tipoconcepto)
                worksheet.write('M' + str(column), nombrecargoencargo)
                worksheet.write('N' + str(column), fechaingreso)
                worksheet.write('O' + str(column), sueldo)
                worksheet.write('P' + str(column), nombrecargo)
                worksheet.write('Q' + str(column), codcargofuncion)
                worksheet.write('R' + str(column), nombreentidad)
                worksheet.write('S' + str(column), codigoentidad)
                worksheet.write('T' + str(column), codigo_sara)
                worksheet.write('U' + str(column), fbasedinero)
            workbook.close()
            buf = base64.b64encode(open('/tmp/' + file_path, 'rb+').read())

            data = header_content + main_content + footer_content
            filename = 'pago_nomina.txt'
            rec.write({'file': base64.b64encode(
                data.encode()), 'file_name': filename,
                'file_sheet': buf,
                'file_sheet_name': file_path})
