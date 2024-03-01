# -*- coding: utf-8 -*-
#############################################################################

#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: ASWIN A K (odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
{
    'name': ' WPS Report Generation for UAE',
    'version': '17.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Open HRMS Wps Payroll System For UAE',
    'description': 'The Wages Protection System(WPS) is an electronic system '
                   'implemented by the GCC Countries to enable transparent '
                   'Wage Payment.This System Generates a Salary '
                   'InformationFile(SIF). And this file is acceptable by'
                   ' the Ministry Of Labour.',
    'author': 'Cybrosys Techno solutions,Open HRMS',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': 'https://www.openhrms.com',
    'depends': [
        'hr_payroll_community',
        'account',
        'hr_holidays',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_employee_views.xml',
        'views/res_bank_views.xml',
        'views/res_company_views.xml',
        'wizard/wps_report_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'uae_wps_report/static/src/js/action_manager.js',
        ],
    },
    'images': ['static/description/banner.jpg'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
