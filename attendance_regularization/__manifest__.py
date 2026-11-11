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
#    This program is distributed in the hope it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#############################################################################
{
    'name': "Open HRMS Attendance Regularization",
    'version': '20.0.1.0.0',
    'category': 'Human Resources/Attendances',
    'summary': 'Manage employee attendance regularization requests for onsite work.',
    'description': """This module enables employees to submit attendance regularization requests for
    onsite work when their attendance is missing or incorrectly recorded. Employees can create requests
    to update their attendance details, which are then reviewed and approved by managers.""",
    'author': 'Cybrosys Techno Solutions, Open HRMS',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': 'https://www.openhrms.com',
    'depends': ['hr_attendance', 'mail'],
    'data': [
        'security/ir.access.csv',
        'data/attendance_regularization_data.xml',
        'views/reg_categories_views.xml',
        'views/attendance_regularization_views.xml',
        'views/hr_attendance_views.xml',
    ],
    'demo': ['demo/attendance_regular_demo.xml'],
    'images': ['static/description/banner.jpg'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
