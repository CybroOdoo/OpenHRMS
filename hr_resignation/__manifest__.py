# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2026-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#############################################################################
{
    'name': 'Open HRMS Resignation',
    'version': '20.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Manages the resignation process of the employees',
    'description': """This module helps to create and approve/reject employee
     resignation requests""",
    'author': 'Cybrosys Techno solutions,Open HRMS',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': 'https://www.openhrms.com',
    'depends': ['hr_employee_updation', 'hr_payroll_community', 'hr_custody', 'survey'],
    'data': [
        'security/ir.access.csv',
        'data/ir_sequence_data.xml',
        'data/ir_cron_data.xml',
        'data/salary_rule_data.xml',
        'views/hr_employee_views.xml',
        'views/hr_resignation_views.xml',
        'views/hr_clearance_views.xml',
        'views/res_config_settings_views.xml',
        'data/mail_template_data.xml',
    ],
    'live_test_url': 'https://youtu.be/BorJthxY_VI',
    'images': ['static/description/banner.jpg'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}
