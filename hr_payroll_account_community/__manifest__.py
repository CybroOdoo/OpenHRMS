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
    'name': 'Odoo20 Payroll Accounting',
    'version': '20.0.1.0.0',
    'category': 'Human Resources',
    'summary': """Helps you to manage payroll and 
     accounting""",
    'description': """Comprehensive solution for managing payroll and accounting processes in Odoo 20.""",
    'test': ['../account/test/account_minimal_test.xml'],
    'author': 'Cybrosys Techno Solutions',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': "https://www.openhrms.com",
    'depends': ['hr_payroll_community', 'account'],
    'data': ['security/ir.access.csv',
             'views/hr_contract_views.xml',
             'wizard/hr_batch_payment_wizard_views.xml',
             'views/hr_payslip_run_views.xml',
             'views/hr_payslip_views.xml',
             'views/hr_salary_rule_views.xml',
             'wizard/hr_payslip_run_generate_views.xml',],
    'images': ['static/description/banner.jpg'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}
