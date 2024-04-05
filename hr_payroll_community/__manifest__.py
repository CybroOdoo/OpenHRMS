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
    'name': 'Odoo 17 HR Payroll',
    'version': '17.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Odoo 17 HR Payroll, payroll, Odoo17 Payroll, Odoo Payroll, Payroll, Odoo17 Payslips, Employee Payroll, HR Payroll,Odoo17, Odoo17 HR, odoo hr,odoo17, Accounting,Odoo Apps',
    'description': "odoo17, Odoo 17 HR Payroll, odoo payroll, odoo17 payroll, payroll community,odoo 17, payroll,Odoo 17 Payroll for Community version where can manage "
                   "Employee Payroll Records",
    'author': 'Cybrosys Techno Solutions',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': 'https://www.openhrms.com',
    'depends': ['hr_contract', 'hr_holidays'],
    'data': [
        'security/hr_payroll_security.xml',
        'security/ir.model.access.csv',
        'data/hr_payroll_sequence.xml',
        'data/hr_payroll_data.xml',
        'wizard/hr_payslips_employees_views.xml',
        'wizard/payslip_lines_contribution_register_views.xml',
        'report/hr_payroll_report.xml',
        'report/report_contribution_register_templates.xml',
        'report/report_payslip_templates.xml',
        'report/report_payslip_details_templates.xml',
        'views/hr_leave_type_views.xml',
        'views/hr_contract_views.xml',
        'views/hr_salary_rule_views.xml',
        'views/hr_salary_rule_category_views.xml',
        'views/hr_contribution_register_views.xml',
        'views/hr_payroll_structure_views.xml',
        'views/hr_payslip_views.xml',
        'views/hr_payslip_line_views.xml',
        'views/hr_employee_views.xml',
        'views/hr_payslip_run_views.xml',
        'views/res_config_settings_views.xml',

    ],
    'demo': ['data/hr_payroll_demo.xml'],
    'images': ['static/description/banner.jpg'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}
