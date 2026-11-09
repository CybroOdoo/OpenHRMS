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
#    This program is distributed in the hope it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#############################################################################
{
    'name': 'Open HRMS Employee History',
    'version': '20.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Track various histories related to an employee',
    'description': """This module tracks the Job/Department History, Salary History,
Contract History and Hourly Cost History of the employees in a company.""",
    'live_test_url': 'https://youtu.be/TaaDrBn3csc',
    'author': 'Cybrosys Techno Solutions, Open HRMS',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': 'https://www.openhrms.com',
    'depends': ['base', 'hr'],
    'data': [
        'security/ir.access.csv',
        'views/contract_history_views.xml',
        'views/department_history_views.xml',
        'views/hr_employee_views.xml',
        'views/salary_history_views.xml',
        'views/hourly_cost_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'history_employee/static/src/scss/timeline_view.scss',
            'history_employee/static/src/js/timeline_view.js',
            'history_employee/static/src/xml/timeline_view.xml',
        ],
    },
    'images': ['static/description/banner.jpg'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
