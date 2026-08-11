# -*- coding: utf-8 -*-
#############################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
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
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
{
    'name': 'Open HRMS Loan Management',
    'version': '19.0.2.0.0',
    'category': 'Human Resources',
    'summary': 'Manage Employee Loan Requests',
    'description': """This module facilitates the creation and management of 
     employee loan requests. The loan amount is automatically deducted from the 
     salary""",
    'author': "Cybrosys Techno Solutions,Open HRMS",
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'live_test_url': 'https://youtu.be/lAT5cqVZTZI',
    'website': "https://cybrosys.com, https://www.openhrms.com",
    'depends': ['hr', 'account', 'hr_payroll_community'],
    'data': [
        'security/hr_loan_security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'data/mail_template_data.xml',
        'data/hr_salary_rule_data.xml',
        'data/hr_rule_input_data.xml',
        'views/hr_loan_views.xml',
        'wizard/hr_loan_early_settlement_views.xml',
        'wizard/hr_loan_deferment_views.xml',
        'wizard/hr_loan_topup_views.xml',
        'views/hr_payslip_views.xml',
        'views/hr_employee_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'demo': [],
    'images': ['static/description/banner.jpg'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
