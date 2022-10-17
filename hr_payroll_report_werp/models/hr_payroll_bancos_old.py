# Copyright 2020-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import datetime
import calendar
from calendar import monthrange

from odoo import api, fields, models, exceptions, _



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


def get_date_combination(month,year):
    date_combination = []
    for date in range(1, 32):
        date_combination.append(year + '-' + month + '-' + str(date).rjust(2, '0'))
    return date_combination

class HrPayrollBancos(models.Model):
    """Hr Payroll Bancos."""
    _name = "hr.payroll.bancos"
    _rec_name = 'month'

    month = fields.Selection(get_months(), string="Month", required=True)
    year = fields.Selection(get_years(), string="Year", required=True)

    def action_generate_report(self):
        for rec in self:
            print("**************", rec)
            print("**************", rec.month)
            print("**************", rec.year)
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
            print (monthText)
            monthDays = monthrange(int(year), int(month))[1]
            init_year = int(year)
            init_month = int(month)
            first_last_day = calendar.monthrange(init_year, init_month)
            if init_month < 7:
                first_day_semester = datetime.datetime(init_year, 1, 1)
            else:
                first_day_semester = datetime.datetime(init_year, 6, 1)
            last_day = datetime.datetime(init_year, init_month, first_last_day[1])

            current_month_first_day = datetime.datetime(int(year), int(month), 1) 
            current_month_last_day = datetime.datetime(int(year), int(month), first_last_day[1])

            first_day = datetime.datetime(int(year), 1, 1)
            CURRENT_MONTH = datetime.datetime.now().month
            CURRENT_YEAR = datetime.datetime.now().year
            df = {}
            voluntary_contribution_novelties = ['Aporte AFC']
            novelties_states = ['processed', 'approved']
            afc_sequences = ['221']
            excluded_voluntary_nits = ['830006270', '8002248088']

            print("######################", get_date_combination(month, year))
            print("@@@@@@@@@@@@@", self.env['hr.payslip'].search([]).date_to)
            df['hr_payslip_prev'] = self.env['hr.payslip'].search([('date_to','in',get_date_combination(month, year))])
            df['hr_payslip'] = self.env['hr.payslip'].search([('date_to','in',get_date_combination(month, year))])
            df['hr_payslip'] = self.env['hr.payslip'].search_read([('date_to','in',get_date_combination(month, year))], ["id", "date_to", "employee_id", "name", "identification_id", "contract_id", "eps_id", "arl_id", "afc_id", "voluntary_contribution_id", "total_amount"])
            # df['hr_payslip_line'] = self.env['hr.payslip.line'].search_read([('slip_id.date_to','in',get_date_combination(month, year))], ["slip_id", "salary_rule_id", "total", "company_id", "name"])
            df['hr_payslip_line'] = self.env['hr.payslip.line'].search_read([], ["slip_id", "salary_rule_id", "total", "company_id", "name"])
            df['hr_salary_rule'] = self.env['hr.salary.rule'].search_read([], ["id", "account_debit", "account_credit", "code_sara", "sequence", "prepaid_medicine_id"])
            print("*******************", df)



            df['account_account'] = self.env['account.account'].search_read([], ["id", "code","name"])

            df['res_company'] = self.env['res.company'].search_read([], ["id", "partner_id", "name"])
            df['res_partner'] = self.env['res.partner'].search_read([], ["id", "vat", "name", "street", "street2", "phone", "email", "l10n_co_document_type"])
            df['macro_area'] = self.env['macro.area'].search_read([], ["id", "name"])
            parent_employee = self.env['hr.employee'].search_read([], ["id", "name", "address_home_id"])
            df['hr_employee'] = self.env['hr.employee'].search_read([], ["id", "macro_area_id", "function_executed_id", "name", "birthday", "place_of_birth", "found_layoffs_id", "pension_fund_id", "entry_date", "job_id", "ident_issuance_city_id", "parent_id", "marital_status_id", "gender", "certificate", "work_email", "work_group_id", "department_id", "arl_percentage", "retention_method_id", "withholding_2", "unemployment_fund_id", "is_dependientes"])
            df['function_executed'] = self.env['function.executed'].search_read([], ["id", "name"])
            df['hr_contract'] = self.env['hr.contract'].search_read([], ["id", "employee_id", "date_start","date_end", "fix_wage_amount", "flex_wage_amount", "wage", "type_id", "struct_id"])
            df['hr_job'] = self.env['hr.job'].search_read([], ["id", "name"])
            df['res_city'] = self.env['res.city'].search_read([], ["id", "name"])
            df['hr_marital_status'] = self.env['hr.marital.status'].search_read([], ["id", "name"])
            df['work_group'] = self.env['work.group'].search_read([], ["id", "name"])
            df['hr_department'] = self.env['hr.department'].search_read([], ["id", "name"])
            df['hr_contract_type'] = self.env['hr.contract.type'].search_read([], ["id", "name"])
            df['hr_payroll_structure'] = self.env['hr.payroll.structure'].search_read([], ["id", "name"])
            df['res_partner_bank'] = self.env['res.partner.bank'].search_read([], ["id", "acc_number", "bank_id","type", "partner_id"])
            df['res_bank'] = self.env['res.bank'].search_read([], ["id", "bic"])
            df['hr_payslip_deductions_rf'] = self.env['hr.payslip.deductions.rf'].search_read([], ["hr_payslip_id","hr_deductions_rf_employee_id"])
            df['hr_deductions_rf_employee'] = self.env['hr.deductions.rf.employee'].search_read([], ["id","hr_deduction_id", "value"])
            df['hr_deduction_rf'] = self.env['hr.deduction.rf'].search_read([], ["id"])
            print("*******************", df)