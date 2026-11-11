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
    'name': 'OpenHRMS Company Policy',
    'version': '20.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Manage Company Policies',
    'description': 'OpenHRMS Company Policies, hrms, policies',
    'author': 'Cybrosys Techno solutions,Open HRMS',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': "https://www.openhrms.com",
    'depends': ['hrms_dashboard'],
    'data': [
        'security/ir.access.csv',
        'views/res_company_views.xml',
        'views/res_company_policy_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'hr_company_policy/static/src/js/company_policy.js',
            'hr_company_policy/static/src/css/company_policy.css',
            'hr_company_policy/static/src/xml/dashboard_view.xml',
        ],
    },
    'images': ['static/description/banner.jpg'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
