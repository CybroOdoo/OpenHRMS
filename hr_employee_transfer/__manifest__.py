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
    'name': 'Open HRMS Branch Transfer',
    'version': '20.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Employee transfer between branches',
    'description': 'This module allows the user to transfer an employee from '
                   'one branch to another branch.',
    'live_test_url': 'https://youtu.be/Qva8kW6xn4c',
    'author': 'Cybrosys Techno Solutions, Open HRMS',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': 'https://www.openhrms.com',
    'depends': ['hr', 'mail'],
    'data': [
        'security/ir.access.csv',
        'views/employee_transfer_views.xml',
    ],
    'images': ['static/description/banner.jpg'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}
