# Copyright 2020-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Hr Payroll Iw Recalc',
    'version': '12.0.1.0.0',
    'summary': 'Hr Payroll Iw Recalc',
    'category': 'Human Resources',
    'author': 'WSuite',
    'license': 'LGPL-3',
    'maintainer': 'WSuite',
    'company': 'WSuite SAS',
    'website': 'https://wsuite.com',
    'depends': [
        'hr_payroll_income_withholding'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/hr_payroll_iw_recalc_data.xml',
        'wizard/add_employees_wizard.xml',
        'wizard/hr_payslip_iw_recalc_add_payslip_wizard.xml',
        'views/hr_payslip_iw_recalc_view.xml',
        'views/inherited_hr_employee_view.xml',
        'views/inherited_hr_value_uvt_view.xml',
        'views/inherited_hr_payslip_view.xml',
    ],
    'installable': True,
}
