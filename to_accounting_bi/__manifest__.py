{
    'name': "Accounting Analysis",
    'name_vi_VN': "Phân tích Kế toán",

    'summary': """
Accounting analysis with Pivot and Graph""",
'summary_vi_VN': """
Phân tích kế toán với giao diện Pivot và Đồ thị""",

    'description': """
Summary
=======
This application provides dynamic accounting reports and analysis in form of pivot and graph views

With this module, you will have a depth analysis of your different financial accounts, analytic accounts. It also provides a treasury report.

Key Features
============

1. Journal Entries Analysis

   - Measures

     * Debit
     * Credit
     * Balance
     * Number of Entries
     * Product Quantity
  
   - Analysis

     * Account Payable Analysis (with Due Date factor)
     * Account Receivable Analysis (with Due Date factor)
     * Entries Analysis by Account
     * Entries Analysis by Account Type
     * Entries Analysis by Product
     * Entries Analysis by Partner
     * Entries Analysis by Currency (in multi-currency environment)
     * Entries Analysis by Company (in multi-company environment)
     * Entries Analysis by Journal
     * Entries Analysis by Analytic Account
     * Entries Analysis by Date
    
2. Treasury Analysis

   - Measures

     * Debit
     * Credit
     * Balance
     
   - Analysis
   
     * Treasury Analysis by Company (in multi-company environment)
     * Treasury Analysis by Journal
     * Treasury Analysis by Entry
     * Treasury Analysis by Partner
     * Treasury Analysis by Date

2. Analytics Entries Analysis

   - Measures

     * Amount / Balance
     * Unit Amount
     * Number of Entries
     
   - Analysis

     * Entries Analysis by Account
     * Entries Analysis by General Account
     * Entries Analysis by Date
     * Entries Analysis by Product
     * Entries Analysis by Partner
     * Entries Analysis by Currency (in multi-currency environment)
     * Entries Analysis by Company (in multi-company environment)
     * Entries Analysis by User
   
Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
     'description_vi_VN': """
Cung cấp khả năng Phân tích động (dạng Business Intelligent) đối với toàn bộ các giao dịch kinh tế được ghi nhận trong hệ thống kế toán.

Với module này, bạn sẽ có một bản phân tích sâu rộng đối với các tài khoản kế toán tài chính, kết toán quản trị, đồng thời cung cấp cả báo cáo ngân sách.

Tính năng chính
===============

1. Phân tích Bút toán Sổ nhật ký

   - Chỉ tiêu

     * Nợ
     * Có
     * Số dư
     * Số lượng Bút toán
     * Số lượng Sản phẩm
  
   - Phân tích

     * Phân tích Kế toán phải Trả (với yếu tố Ngày đến hạn)
     * Phân tích Kế toán phải Thu (với yếu tố Ngày đến hạn)
     * Phân tích Bút toán theo Tài khoản
     * Phân tích Bút toán theo Kiểu Tài khoản
     * Phân tích Bút toán theo Sản phẩm
     * Phân tích Bút toán theo Đối tác (Khách hàng, Nhà cung cấp, v.v.)
     * Phân tích Bút toán theo Tiền tệ (trong môi trường đa tiền tệ)
     * Phân tích Bút toán theo Công ty (trong môi trường đa công ty)
     * Phân tích Bút toán theo Sổ Nhật ký
     * Phân tích Bút toán theo Tài khoản Quản trị
     * Phân tích Bút toán theo Ngày vào sổ
    
2. Phân tích Ngân sách

   - Chỉ tiêu

     * Nợ
     * Có
     * Số dư
     
   - Phân tích
   
     * Phân tích Ngân sách theo Công ty (trong môi trường đa công ty)
     * Phân tích Ngân sách theo Sổ nhật ký
     * Phân tích Ngân sách theo Bút toán
     * Phân tích Ngân sách theo Đối tác (Khách hàng, Nhà cung cấp, v.v.)
     * Phân tích Ngân sách theo Ngày vào sổ các phát sinh

2. Phân tích Bút toán Quản trị

   - Chỉ tiêu

     * Giá trị / Số dư
     * Đơn giá
     * Số lượng bút toán
     
   - Phân tích

     * Phân tích Bút toán Quản trị theo Tài khoản Quản trị
     * Phân tích Bút toán Quản trị theo Tài khoản KT Tài chính
     * Phân tích Bút toán Quản trị theo Ngày vào sổ
     * Phân tích Bút toán Quản trị theo Sản phẩm 
     * Phân tích Bút toán Quản trị theo Đối tác (Khách hàng, Nhà cung cấp, v.v.)
     * Phân tích Bút toán Quản trị theo Tiền tệ (trong môi trường đa tiền tệ)
     * Phân tích Bút toán Quản trị theo Công ty (trong môi trường đa công ty)
     * Phân tích Bút toán Quản trị theo Người dùng 

Phiên bản hỗ trợ
================
1. Community Edition
2. Enterprise Edition

    """,

    'author': "T.V.T Marine Automation (aka TVTMA)",
    'website': 'https://www.tvtmarine.com',
    'live_test_url': 'https://v12demo-int.erponline.vn',
    'support': 'support@ma.tvtmarine.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting & Finance',
    'version': '1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/account_entries_analysis.xml',
        'views/account_treasury_report.xml',
        'views/account_analytic_entries_report.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': 49.5,
    'currency': 'EUR',
    'license': 'OPL-1',
}