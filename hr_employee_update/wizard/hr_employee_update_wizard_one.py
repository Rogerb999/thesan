# -*- encoding: utf-8 -*-

import base64
import xlrd
from odoo import api, fields, models
from datetime import datetime


class HrEmployeeUpdateWizardOne(models.TransientModel):
    _name = 'hr.employee.update.wizard.one'

    excel_file = fields.Binary('Employee Excel Data', required=1)

    @api.multi
    def data_import(self):
        wb = xlrd.open_workbook(
            file_contents=base64.decodestring(self.excel_file))
        row_list = []
        last_sheet = wb.sheet_by_index(0)
        # Will pick first sheet of the Excel Workbook
        for row in range(3, last_sheet.nrows):
            row_list.append(last_sheet.row_values(row))
        for employee_list in row_list:
            if employee_list[4] and employee_list[4] != '.':
                employee_id = self.env['hr.employee'].search(
                    [('identification_id', '=', employee_list[4])],
                    limit=1)
                if employee_id:
                    partner = self.env['res.partner'].search(
                        [('vat', '=', employee_list[4])], limit=1)
                    if partner:
                        if employee_list[4] and employee_list[4] != '.':
                            if partner.vat != employee_list[4]:
                                partner.write({'vat': employee_list[4]})
                        if employee_list[15] and employee_list[15] != '.':
                            employee_list[15] = employee_list[15].strip()
                            if partner.street != employee_list[15]:
                                partner.write({'street': employee_list[15]})
                        if employee_list[16] and employee_list[16] != '.':
                            employee_list[16] = employee_list[16].strip()
                            if partner.street2 != employee_list[16]:
                                partner.write({'street2': employee_list[16]})
                        if employee_list[26] and employee_list[26] != '.':
                            employee_list[26] = employee_list[26].strip()
                            if partner.email != employee_list[26]:
                                partner.write({'email': employee_list[26]})
                        if employee_list[17] and employee_list[17] != '.':
                            employee_list[17] = employee_list[17].strip()
                            if partner.phone != employee_list[17]:
                                partner.write({'phone': employee_list[17]})
                    if employee_list[7] and employee_list[7] != '.':
                        employee_list[7] = employee_list[7].strip()
                        res_city_id = self.env['res.city'].search(
                            [('name', 'ilike', employee_list[7])], limit=1)
                        if res_city_id:
                            if employee_id.ident_issuance_city_id.name !=\
                                    res_city_id.name:
                                employee_id.write(
                                    {'ident_issuance_city_id': res_city_id.id})
                    if employee_list[18] and employee_list[18] != '.':
                        birthday = employee_list[18]
                        birthday = datetime(*xlrd.xldate_as_tuple(
                            birthday, 0)).date()
                        if employee_id.birthday != birthday:
                            employee_id.write({'birthday': birthday})
                    if employee_list[19] and employee_list[19] != '.':
                        employee_list[19] = employee_list[19].strip()
                        place_of_birth_id = self.env['res.city'].search(
                            [('name', 'ilike', employee_list[19])], limit=1)
                        if place_of_birth_id:
                            if employee_id.place_of_birth_id.name !=\
                                    place_of_birth_id.name:
                                employee_id.write(
                                    {'place_of_birth_id': place_of_birth_id.id
                                     })
                    if employee_list[20] and employee_list[20] != '.':
                        employee_list[20] = employee_list[20].strip()
                        hr_marital_status_id = self.env[
                            'hr.marital.status'].search([
                                ('name', '=ilike',
                                    employee_list[20] + '%')], limit=1)
                        if hr_marital_status_id:
                            if employee_id.marital_status_id.name !=\
                                    hr_marital_status_id.name:
                                employee_id.write(
                                    {'marital_status_id':
                                     hr_marital_status_id.id})
                    if employee_list[21] and employee_list[21] != '.':
                        data_gender = False
                        if employee_list[21] == 'M':
                            data_gender = 'male'
                        if employee_list[21] == 'F':
                            data_gender = 'female'
                        if employee_list[21] == 'O':
                            data_gender = 'other'
                        if employee_id.gender != data_gender and data_gender:
                            employee_id.write({'gender': data_gender})
                    if employee_list[23] and employee_list[23] != '.':
                        employee_list[23] = employee_list[23].strip()
                        hr_academic_level_id = self.env[
                            'hr.academic.level'].search(
                            [('name', '=ilike', employee_list[23] + '%')],
                            limit=1)
                        if hr_academic_level_id:
                            if employee_id.academic_level_id.name !=\
                                    hr_academic_level_id.name:
                                employee_id.write(
                                    {'academic_level_id':
                                     hr_academic_level_id.id})
                    if employee_list[28] and employee_list[28] != '.':
                        employee_list[28] = employee_list[28].strip()
                        unity_id = self.env['hr.employee.unity'].search(
                            [('name', '=ilike', employee_list[28] + '%')],
                            limit=1)
                        if unity_id:
                            if employee_id.unity_id.name != unity_id.name:
                                employee_id.write({'unity_id': unity_id.id})
                    if employee_list[30] and employee_list[30] != '.':
                        employee_list[30] = employee_list[30].strip()
                        zone_id = self.env['hr.employee.zone'].search(
                            [('name', '=ilike', employee_list[30] + '%')],
                            limit=1)
                        if zone_id:
                            if employee_id.zone_id.name != zone_id.name:
                                employee_id.write({'zone_id': zone_id.id})
                    if employee_list[32] and employee_list[32] != '.':
                        employee_list[32] = employee_list[32].strip()
                        cost_center_id = self.env['hr.cost.center'].search(
                            [('name', '=ilike', employee_list[32] + '%')],
                            limit=1)
                        if cost_center_id:
                            if employee_id.cost_center_id.name !=\
                                    cost_center_id.name:
                                employee_id.write(
                                    {'cost_center_id': cost_center_id.id})
                    if employee_list[34] and employee_list[34] != '.':
                        employee_list[34] = employee_list[34].strip()
                        cost_line_id = self.env['hr.cost.line'].search(
                            [('name', '=ilike', employee_list[34] + '%')],
                            limit=1)
                        if cost_line_id:
                            if employee_id.cost_line_id.name !=\
                                    cost_line_id.name:
                                employee_id.write(
                                    {'cost_line_id': cost_line_id.id})
                    if employee_list[39] and employee_list[39] != '.':
                        employee_list[39] = employee_list[39].strip()
                        employment_relationship_id = self.env[
                            'hr.employment.relationship'].search(
                            [('name', '=ilike', employee_list[39] + '%')],
                            limit=1)
                        if employment_relationship_id:
                            if employee_id.employment_relationship_id.name !=\
                                    employment_relationship_id.name:
                                employee_id.write(
                                    {'employment_relationship_id':
                                     employment_relationship_id.id})
                    if employee_list[42] and employee_list[42] != '.':
                        entry_date = employee_list[42]
                        entry_date = datetime(*xlrd.xldate_as_tuple(
                            entry_date, 0)).date()
                        if employee_id.entry_date != entry_date:
                            employee_id.write({'entry_date': entry_date})
                    if employee_list[48] and employee_list[48] != '.':
                        employee_list[48] = employee_list[48].strip()
                        if employee_id.code_office != employee_list[48]:
                            employee_id.write(
                                {'code_office': employee_list[48]})
                    if employee_list[50] and employee_list[50] != '.':
                        salary_effective_date = employee_list[50]
                        salary_effective_date = datetime(*xlrd.xldate_as_tuple(
                            salary_effective_date, 0)).date()
                        if employee_id.salary_effective_date !=\
                                salary_effective_date:
                            employee_id.write(
                                {'salary_effective_date':
                                 salary_effective_date})
                    if employee_list[54] and employee_list[54] != '.':
                        employee_list[54] = employee_list[54].strip()
                        bank_account_id = self.env[
                            'res.partner.bank'].search(
                            [('acc_number', '=ilike',
                                employee_list[54] + '%')],
                            limit=1)
                        if not bank_account_id and employee_id.bank_account_id:
                            bank_account_id = employee_id.bank_account_id
                            bank_account_id.write({
                                'acc_number': employee_list[54]})
                        if bank_account_id:
                            if employee_id.bank_account_id.id !=\
                                    bank_account_id.id:
                                employee_id.write(
                                    {'bank_account_id': bank_account_id.id})
                            if employee_list[56] and employee_list[56] != '.':
                                employee_list[56] = str(
                                    employee_list[56]).strip()
                                if employee_id.bank_account_id.bank_bic !=\
                                        bank_account_id.bank_bic:
                                    employee_id.bank_account_id.write(
                                        {'bank_bic': employee_list[56]})
                            if employee_list[57] and employee_list[57] != '.':
                                employee_list[57] = employee_list[57].strip()
                                bank_id = self.env['res.bank'].search(
                                    [('name', '=ilike',
                                        employee_list[57] + '%')],
                                    limit=1)
                                if bank_id:
                                    if employee_id.\
                                        bank_account_id.bank_id.name !=\
                                            bank_id.name:
                                        employee_id.bank_account_id.write(
                                            {'bank_id': bank_id.id})
                            if employee_list[58] and employee_list[58] != '.':
                                employee_list[58] = employee_list[58].strip()
                                data_bank_type = False
                                if employee_list[58] == 'CA':
                                    data_bank_type = 'savings'
                                if employee_list[58] == 'CC':
                                    data_bank_type = 'current'
                                if employee_id.bank_account_id.type !=\
                                        data_bank_type and\
                                        data_bank_type:
                                    employee_id.bank_account_id.write(
                                        {'type': data_bank_type})
                    if employee_list[59] and employee_list[59] != '.':
                        employee_list[59] = employee_list[59].strip()
                        eps_id = self.env['res.partner'].search(
                            [('name', '=ilike', employee_list[59] + '%')],
                            limit=1)
                        if eps_id:
                            if employee_id.eps_id.name != eps_id.name:
                                employee_id.write({'eps_id': eps_id.id})
                    if employee_list[60] and employee_list[60] != '.':
                        employee_list[60] = employee_list[60].strip()
                        pension_fund_id = self.env['res.partner'].search(
                            [('name', '=ilike', employee_list[60] + '%')],
                            limit=1)
                        if pension_fund_id:
                            if employee_id.pension_fund_id.name !=\
                                    pension_fund_id.name:
                                employee_id.write(
                                    {'pension_fund_id': pension_fund_id.id})
                    if employee_list[61] and employee_list[61] != '.':
                        employee_list[61] = employee_list[61].strip()
                        found_layoffs_id = self.env['res.partner'].search(
                            [('name', '=ilike', employee_list[61] + '%')],
                            limit=1)
                        if found_layoffs_id:
                            if employee_id.found_layoffs_id.name !=\
                                    found_layoffs_id.name:
                                employee_id.write(
                                    {'found_layoffs_id': found_layoffs_id.id})
                    if employee_list[62] and employee_list[62] != '.':
                        employee_list[62] = employee_list[62].strip()
                        unemployment_fund_id = self.env['res.partner'].search(
                            [('name', '=ilike', employee_list[62] + '%')],
                            limit=1)
                        if unemployment_fund_id:
                            if employee_id.unemployment_fund_id.name !=\
                                    unemployment_fund_id.name:
                                employee_id.write(
                                    {'unemployment_fund_id':
                                     unemployment_fund_id.id})
                    if employee_list[63] and employee_list[63] != '.':
                        employee_list[63] = employee_list[63].strip()
                        arl_id = self.env['res.partner'].search(
                            [('name', '=ilike', employee_list[63] + '%')],
                            limit=1)
                        if not arl_id:
                            arl_id = self.env['res.partner'].create({
                                'name': employee_list[63],
                                'is_arl': 1})
                        if arl_id:
                            if employee_id.arl_id.name != arl_id.name:
                                employee_id.write({'arl_id': arl_id.id})
                    contract = self.env['hr.contract'].search([
                        ('state', '=', 'open'),
                        ('employee_id', '=', employee_id.id)],
                        order='create_date DESC', limit=1)
                    if contract:
                        if employee_list[40] and employee_list[40] != '.':
                            date_start = employee_list[40]
                            date_start = datetime(*xlrd.xldate_as_tuple(
                                date_start, 0)).date()
                            if contract.date_start != date_start:
                                contract.write({'date_end': False})
                                contract.write({'date_start': date_start})
                        if employee_list[43] and employee_list[43] != '.':
                            date_end = employee_list[43]
                            date_end = datetime(*xlrd.xldate_as_tuple(
                                date_end, 0)).date()
                            if contract.date_end != date_end:
                                contract.write({'date_end': date_end})
                        if employee_list[64] and employee_list[64] != '.':
                            employee_list[64] = str(employee_list[64])
                            employee_list[64] = float(
                                employee_list[64].strip().replace('%', ''))
                            if contract.arl_percentage != employee_list[64]:
                                contract.write({
                                    'arl_percentage': employee_list[64]})
                        if employee_list[77] and employee_list[77] != '.':
                            employee_list[77] = employee_list[77].strip()
                            recruitment_reason_id = self.env[
                                'recruitment.reason'].search(
                                [('name', '=ilike', employee_list[77] + '%')],
                                limit=1)
                            if not recruitment_reason_id:
                                recruitment_reason_id = self.env[
                                    'recruitment.reason'].create({
                                        'name': employee_list[77]})
                            if recruitment_reason_id:
                                if contract.recruitment_reason_id.name !=\
                                        employee_list[77]:
                                    contract.write({
                                        'recruitment_reason_id':
                                        recruitment_reason_id.id})
