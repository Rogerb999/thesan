# -*- coding: utf-8 -*-
{
    'name': "ReportMate",

    'summary': """
        ReportMate shows complex data in a single view, and you do not have to click repeatedly to get the required results.
 """,

    'description': """
        Best Custom Report Apps
        Custom Report Apps
        Custom Reports
        Report Mate
        Custom View Apps
        Report Maker
        Custom Field
        Tree View Report
        Tree View Model
        Tree View Table
        Odoo View
        Odoo Form
        Table View
        Sales Custom Report
        Product Custom Report
        Odoo Custom Report Apps
        List View Model
        List View Report
        List View Table
        Pivot View Report
        Pivot View Model
        Pivot View Table
        Graph View Model
        Graph View Report
        Graph View Table
        Custom Report Creator Apps
        GTS Custom report
        Financial Report
        Move Report
        Flat Data Structure View
        Widget View
        Sale order custom report.
        Report View Apps
        Report Creator Apps
        Custom Report Creator Apps
        ReportMate Report
    """,
    'author': "Ksolves India Pvt. Ltd.",
    'license': 'OPL-1',
    'currency': 'EUR',
    'price': 79.0,
    'website': "https://www.ksolves.com",
    'maintainer': 'Ksolves India Pvt. Ltd.',
    'category': 'Tools',
    'version': '12.0.1.0.1',
    'support': 'sales@ksolves.com',
    'images': ['static/description/banner_1.gif'],
    'live_test_url': 'https://reportmate.kappso.com/request/demo',

    'depends': ['base'],

    'data': [
        'security/ks_security_groups.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/ks_assets_backend.xml',
    ],

    'installable': True,
    'application': True,

    'uninstall_hook': 'uninstall_hook',

}
