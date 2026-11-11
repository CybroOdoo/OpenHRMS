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
    'name': 'Open HRMS Leave Multi-Level Approval',
    'version': '20.0.1.0.0',
    'category': 'Human Resources',
    'summary': """Efficient multi-level leave approval system for seamless request processing.""",
    'description': """Elevate your leave request process with this module. 
     Empower employees to submit requests, while providing supervisors at 
     various levels the ability to review, approve, or reject seamlessly.""",
    'author': 'Cybrosys Techno Solutions, Open HRMS',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': "https://www.openhrms.com",
    'depends': ['hr_holidays', 'hr_work_entry'],
    'data': [
        'security/ir.access.csv',
        'views/hr_leave_views.xml',
        'views/hr_work_entry_type_views.xml',
        'views/hr_holidays_validators_views.xml',
    ],
    'images': ['static/description/banner.jpg'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
