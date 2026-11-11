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
    'name': 'Open HRMS Employee Insurance',
    'version': '20.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Employee Insurance Management for Open HRMS.',
    'description': 'Manages insurance amounts for employees to be deducted from salary.',
    'author': 'Cybrosys Techno Solutions',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': 'https://www.openhrms.com',
    'depends': [
        'base',
        'hr',
        'mail',
        'hr_payroll_community',
        'hr_employee_updation',
    ],
    'data': [
        'security/ir.access.csv',
        'data/hr_salary_rule_data.xml',
        'data/hr_insurance_cron.xml',
        'views/insurance_policy_views.xml',
        'views/employee_insurance_views.xml',
        'views/hr_employee_views.xml',
    ],
    'images': ['static/description/banner.jpg'],
    'license': 'LGPL-3',
}
