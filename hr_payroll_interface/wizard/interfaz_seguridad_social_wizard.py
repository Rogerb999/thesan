# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import xlsxwriter
import base64

from odoo import api, fields, models, _


class InterfazSeguridadSocialWizard(models.TransientModel):
    """Interfaz Seguridad Social Wizard."""

    _name = 'interfaz.seguridad.social.wizard'
    _description = "Seguridad Social Wizard"

    document = fields.Binary('Documents')
    file = fields.Char('Report File Name', readonly=1)

    @api.multi
    def report_excel(self):
        """Print the Excel Report."""
        for rec in self:
            file_path = 'work_in_progress' + '.xlsx'
            workbook = xlsxwriter.Workbook('/tmp/' + file_path)
            worksheet = workbook.add_worksheet("Work in Progress")
            worksheet.write('A1', _('Type'))
            worksheet.write('B1', _('Number'))
            worksheet.write('C1', _('Item'))
            worksheet.write('D1', _('Date'))
            worksheet.write('E1', _('Numberaccount'))
            worksheet.write('F1', _('Nittercero'))
            worksheet.write('G1', _('Cheque'))
            worksheet.write('H1', _('Debit'))
            worksheet.write('I1', _('Credit'))
            worksheet.write('J1', _('AccountName'))
            worksheet.write('K1', _('Base'))
            worksheet.write('L1', _('CostCenter'))
            worksheet.write('M1', _('CLipro'))
            worksheet.write('N1', _('Company'))
            worksheet.write('O1', _('Auxiliar'))
            worksheet.write('P1', _('Salarytype'))
            worksheet.write('Q1', _('EconomicZone'))
            worksheet.write('R1', _('NCOM'))
            worksheet.write('S1', _('CODEMPRESA'))
            payroll_rec = self.env[self._context.get('active_model')].browse(
                self._context.get('active_id'))
            column = 1
            for line in payroll_rec.payslip_ids:
                column += 1
                worksheet.write('N' + str(column), line.company_id.name)

            workbook.close()
            buf = base64.b64encode(open('/tmp/' + file_path, 'rb+').read())
            rec.document = buf
            rec.file = 'INTERFAZ SEGURIDAD SOCIAL ' + \
                self.env.user.company_id.name + ' ' +\
                rec.create_date.strftime(
                    '%Y') + '-' + rec.create_date.strftime('%B') + '.xlsx'
            return {
                'res_id': rec.id,
                'name': 'Files to Download',
                'view_type': 'form',
                "view_mode": 'form,tree',
                'res_model': 'interfaz.seguridad.social.wizard',
                'type': 'ir.actions.act_window',
                'target': 'new',
            }
