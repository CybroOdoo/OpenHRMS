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
    'name': "Open HRMS Employee Shift",
    'version': '20.0.1.0.0',
    'summary': """Easily create, manage, and track employee shift schedules.""",
    'description': """It helps manage and track employee shifts and schedule 
        them according to their contracts and work requirements.""",
    'live_test_url': 'https://youtu.be/o580wqD9Nig',
    'category': 'Human Resource',
    'author': 'Cybrosys Techno solutions,Open HRMS',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': "https://www.openhrms.com",
    'depends': ['hr_payroll_community', 'resource'],
    'data': [
        'security/ir.access.csv',
        'data/cron.xml',
        'wizard/hr_generate_shift_views.xml',
        'views/hr_employee_shift_views.xml',
        'views/hr_employee_views.xml',
    ],
    'demo': [
        'demo/shift_schedule_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'hr_employee_shift/static/src/css/shift_dashboard.css',
            'hr_employee_shift/static/src/scss/shift_dashboard.scss',
            'hr_employee_shift/static/src/js/shift_kanban.js',
            'hr_employee_shift/static/src/xml/shift_kanban.xml',
        ],
    },
    'images': ["static/description/banner.jpg"],
    'license': "LGPL-3",
    'installable': True,
    'auto_install': False,
    'application': True,
}
