# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'HR Employee Payslip Reports (PDF/Excel)',
    'version': '12.0.0.0',
    'author': 'BrowseInfo',
    'website': 'https://www.browseinfo.in',
    'category': 'Human Resources',
    'summary': 'Employee Multiple Payslip Report print employee payslip report hr payslip report employee pay slip report mass employee payslip report print payslip report print employee payroll report print pay slip report print payslip excel report payslip xls report',
    'description': """ 
            
               Employee Multiple Payslip Report PDF & XLS  in odoo,
               Multiple payslip report pdf in odoo,
               Multiple payslip report xls in odoo,
               Salary computation Group by Salary Rule Category in odoo,
               Salary computation Group by Salary Rule in odoo,
               Print Payslip Report by PDF & XLS File Type in odoo,
               
    """,
    'depends':['hr_payroll'],
    'data':[
        'wizard/payslip_report_wizard.xml',
        'report/employee_payslip_report.xml',
        'report/payslip_report_template.xml',
        ],
    'price': 15,
    'currency': 'EUR',
    'installable': True,
    'auto_install': False,
    'live_test_url':'https://youtu.be/5R0Ny75MEfI',
    'images':['static/description/Banner.png'],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
