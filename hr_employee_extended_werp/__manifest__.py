# -*- coding: utf-8 -*-
# Copyright 2019-TODAY WSuite Products <wsuite-products@wsuite.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Hr Employee Extended WSuite',
    'version': '12.0.1.0.0',
    'summary': 'Extends the Hr Employee Functionality for WSuite',
    'category': 'Human Resources',
    'author': 'WSuite',
    'license': 'LGPL-3',
    'maintainer': 'WSuite',
    'company': 'WSuite SAS',
    'website': 'https://wsuite.com/',
    'depends': [
               'hr_recruitment',
    ],
    'data': [
        'data/ir_cron_data.xml',
        'views/animal_type_view.xml',
        'views/animal_race.xml',
        'views/animal_pet.xml',
        'wizard/report_employee_wizard_views.xml',
        'views/hr_employment_relationship_view.xml',
        'views/hr_employee_unity_view.xml',
        'views/hr_employee_zone_view.xml',
        'views/hr_cost_center_view.xml',
        'views/hr_cost_line_view.xml',
        'views/hr_arl_level_view.xml',
        'views/hr_arl_view.xml',
        'views/hr_cotract_type_view.xml',
        'views/hr_employee_view.xml',
        'views/inherited_hr_contract_view.xml',
        'views/report_model_config_view.xml',
        'views/res_config_settings_views.xml',
        'security/ir.model.access.csv',
        'views/inherited_hr_department_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
