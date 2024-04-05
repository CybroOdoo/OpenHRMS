# -*- coding: utf-8 -*-
#############################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
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
    'name': 'Odoo17 Payroll Accounting',
    'version': '17.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Odoo 17 HR Payroll, payroll, Odoo17 Payroll, Odoo Payroll, Payroll, Odoo17 Payslips, Employee Payroll, HR Payroll,Odoo17, Odoo17 HR, odoo hr,odoo17, Accounting,Odoo Apps',
    'description': """ This module helps you to manage payroll and 
     accounting.""",
    'test': ['../account/test/account_minimal_test.xml'],
    'author': 'Cybrosys Techno Solutions',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': "https://www.openhrms.com",
    'depends': ['hr_payroll_community', 'account'],
    'data': ['views/hr_contract_views.xml',
             'views/hr_payslip_run_views.xml',
             'views/hr_payslip_views.xml',
             'views/hr_salary_rule_views.xml', ],
    'images': ['static/description/banner.jpg'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
