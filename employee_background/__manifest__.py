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
    'name': 'Open HRMS Employee Background Verification',
    'version': '20.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Verify background details and documents of employees.',
    'description': """Manage the employee background verification process with
    agency assignments, portal submissions, and verification tracking.""",
    'live_test_url': 'https://youtu.be/mH5SzuKHa30',
    'author': 'Cybrosys Techno Solutions, Open HRMS',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': 'https://www.openhrms.com',
    'depends': [
        'hr',
        'mail',
        'portal',
        'website',
    ],
    'data': [
        'security/ir.access.csv',
        'data/ir_sequence_data.xml',
        'data/mail_template_data.xml',
        'data/portal_entry_data.xml',
        'views/employee_verification_portal_templates.xml',
        'views/employee_verification_views.xml',
        'views/res_partner_views.xml',
    ],
    'demo': [
        'demo/employee_verification_demo.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'employee_background/static/src/interactions/employee_background_portal.js',
        ],
    },
    'images': ['static/description/banner.jpg'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
